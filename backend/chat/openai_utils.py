import os
import json
import openai
import asyncio
import traceback

from asgiref.sync import sync_to_async
from .db_lookup import perform_db_lookup
from .models import ChatMessage, ChatSession

openai.api_key = os.getenv("OPENAI_API_KEY")

MODEL_METADATA = {
    "Order": ["id", "customer", "status", "created_at", "requested_by"],
    "OrderItem": ["id", "order", "product", "quantity", "price"],
    "Customer": ["id", "name", "email", "phone", "created_at"],
    "Product": ["id", "name", "price", "category", "description", "stock_quantity"]
}

FUNCTIONS = [
    {
        "name": "run_sql_query",
        "description": "Perform a dynamic database lookup based on a lookup specification.",
        "parameters": {
            "type": "object",
            "properties": {
                "lookup_spec": {
                    "type": "object",
                    "description": (
                        "A lookup specification with keys: 'model', 'filters', and 'fields'. "
                        "For example: {\"model\": \"Order\", \"filters\": {\"status\": \"delivered\"}, "
                        "\"fields\": [\"id\", \"customer__name\", \"status\", \"created_at\"]}"
                    ),
                }
            },
            "required": ["lookup_spec"],
        },
    }
]

def build_system_prompt():
    models_info = "\n".join(
        [f"- {model}: {', '.join(fields)}" for model, fields in MODEL_METADATA.items()]
    )
    return (
        "You are an AI assistant for a retail application. "
        "You have access to these django models:\n"
        f"{models_info}\n\n"
        "Important instructions:\n"
        "1. Interpret 'jobs' or 'job' as 'orders' in user queries.\n"
        "2. If the user says 'delayed' or 'pending', interpret that as {\"status__iexact\": \"pending\"}.\n"
        "3. When the user asks about orders, default to model 'Order'.\n"
        "4. When the user asks about order items, default to model 'OrderItem'.\n"
        "5. When the user asks about customers, default to model 'Customer'.\n"
        "6. When the user asks about products, default to model 'Product'.\n"
        "7. If the user mentions a customer name (e.g. 'John'), use a filter like "
        "{\"customer__name__icontains\": \"john\"}.\n"
        "8. Whenever the user requests specific data, you MUST call 'run_sql_query'.\n\n"
        "9. If the function_call result is an empty list (i.e., '[]'), respond with:"
        "   'No records found for your query.'"
        "10. If the function_call result is not empty, summarize the results and provide a relevant answer."
        "Use relevant fields from each model to craft the lookup. Only pick from the known fields.\n"
        "Steps:\n"
        "1) If you need to call a function to do a database lookup, do so with 'run_sql_query' and provide:\n"
        "   - model\n"
        "   - filters\n"
        "   - fields\n\n"
        "2) After receiving the function result, provide a final answer.\n\n"
        "3) If a user references a non-existent field, interpret it in the closest valid way.\n"
    )

async def async_call_openai_chat(messages, functions=None, function_call="auto"):
    """
    A thin wrapper around openai.ChatCompletion.create() executed in a thread,
    allowing us to call it from async code without blocking.
    """
    return await asyncio.to_thread(
        openai.ChatCompletion.create,
        model="gpt-3.5-turbo",
        messages=messages,
        functions=functions,
        function_call=function_call
    )

def format_function_response(function_name: str, content: dict):
    """
    Format the function response message to feed back into the conversation
    so the assistant can provide a final answer.
    """
    return {
        "role": "function",
        "name": function_name,
        "content": json.dumps(content)
    }

async def process_conversation(user_query, session_id, user=None):
    """
    - Loads up to last 10 messages from ChatMessage for context
    - Calls OpenAI (1st call)
    - If a function is requested, run it, then call OpenAI again (2nd call) with function role message
    - Return a final reply
    """
    try:
        # 1. Validate session
        session = await sync_to_async(ChatSession.objects.filter)(session_id=session_id)
        session = await sync_to_async(session.first)()
        if not session:
            return {"error": "Invalid session ID."}

        # 2. Load chat history
        recent_messages = await sync_to_async(list)(
            ChatMessage.objects.filter(session=session).order_by("-created_at")[:10]
        )

        chat_history = []
        for msg in reversed(recent_messages):
            content = msg.content if msg.content is not None else ""
            chat_history.append({"role": msg.role, "content": content})


        # 3. Build the conversation: system + history + new user query
        messages = [{"role": "system", "content": build_system_prompt()}] + chat_history
        messages.append({"role": "user", "content": user_query})

        # Save the user's message
        await sync_to_async(ChatMessage.objects.create)(
            session=session, role="user", content=user_query
        )

        # ---------------------------
        # 4. First call to OpenAI
        # ---------------------------
        initial_response = await async_call_openai_chat(messages, functions=FUNCTIONS, function_call="auto")
        first_assistant_msg = initial_response["choices"][0]["message"]

        print(first_assistant_msg)

        # Extract potential function call
        func_call = first_assistant_msg.get("function_call")
        assistant_reply = first_assistant_msg.get("content") or ""

        if func_call:
            # ================
            # 4a. There's a function call
            # ================
            function_name = func_call["name"]
            raw_args = func_call.get("arguments", "{}")

            # Attempt to parse function arguments
            try:
                args_dict = json.loads(raw_args)
            except json.JSONDecodeError:
                error_msg = "Function call error: Invalid JSON arguments."
                await sync_to_async(ChatMessage.objects.create)(
                    session=session, role="assistant", content=error_msg
                )
                return {"reply": error_msg}

            # Make sure we have a dict
            if not isinstance(args_dict, dict):
                error_msg = "Function call error: arguments must be a JSON object."
                await sync_to_async(ChatMessage.objects.create)(
                    session=session, role="assistant", content=error_msg
                )
                return {"reply": error_msg}

            # 5. Perform the actual function logic (db_lookup)
            if function_name == "run_sql_query":
                lookup_spec = args_dict.get("lookup_spec", args_dict)
                print("DEBUG function_name:", function_name)
                print("DEBUG lookup_spec:", lookup_spec)
                db_results = await perform_db_lookup(lookup_spec)
                print("DEBUG db_results from perform_db_lookup:", db_results)

                # Format or store db_results
                # We'll feed it back to the assistant as a function role message
                function_msg = format_function_response(function_name, db_results)

                # Append the function role message so the assistant can finalize the reply
                messages.append(first_assistant_msg)  # The assistant function call
                messages.append(function_msg)         # The function result

                # ---------------------------
                # 5a. Second call to OpenAI
                # ---------------------------
                second_response = await async_call_openai_chat(
                    messages,
                    functions=FUNCTIONS,
                    function_call="auto"
                )

                second_assistant_msg = second_response["choices"][0]["message"]
                final_text = second_assistant_msg.get("content", "")

                # Save final assistant response
                await sync_to_async(ChatMessage.objects.create)(
                    session=session, role="assistant", content=final_text
                )
                return {"reply": final_text or "No final answer provided."}
            else:
                # Unsupported function, just respond with an error
                error_msg = f"Unknown function: {function_name}"
                await sync_to_async(ChatMessage.objects.create)(
                    session=session, role="assistant", content=error_msg
                )
                return {"reply": error_msg}
        else:
            # ================
            # 4b. No function call
            # ================
            if not assistant_reply.strip():
                # If there's truly no text, provide a fallback
                assistant_reply = "I'm not sure how to respond. Could you clarify?"

            # Save final assistant response
            await sync_to_async(ChatMessage.objects.create)(
                session=session, role="assistant", content=assistant_reply
            )
            return {"reply": assistant_reply}
    except Exception as e:
        # Log the traceback, store a user-friendly message
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        await sync_to_async(ChatMessage.objects.create)(
            session=session, role="assistant", content=error_message
        )
        return {"reply": "Something went wrong. Our team has been notified."}

