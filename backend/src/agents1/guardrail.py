from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types  # For creating response content


def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for blocked keywords. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = (
        callback_context.agent_name
    )  # Get the name of the agent whose model call is being intercepted
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break  # Found the last user message text

    print(
        f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---"
    )  # Log first 100 chars

    # --- Guardrail Logic ---
    keywords_to_block = ["BLOCK"]
    for keyword in keywords_to_block:
        if keyword in last_user_message_text.upper():  # Case-insensitive check
            print(f"--- Callback: Found '{keyword}'. Blocking LLM call! ---")
            # Optionally, set a flag in state to record the block event
            callback_context.state["guardrail_block_keyword_triggered"] = True
            print(
                "--- Callback: Set state 'guardrail_block_keyword_triggered': True ---"
            )
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(
                            text=f"I'm sorry, I cannot process this request because it contains the blocked keyword '{keyword}'."
                        )
                    ],
                )
            )

    # If no blocked keywords found, return None to proceed
    return None
