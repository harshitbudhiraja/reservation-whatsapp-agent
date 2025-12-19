import json
from agents.intent_classify import classify_intent
from agents.parameter_extractor import extract_parameters
from utils.conversation_state import conversation_state
from utils.message_templates import FUNCTION_REQUIRED_PARAMS, get_missing_params_message
from utils.booking_utils import book_table

class AgentOrchestrator:
    def process(self, user_input: str, user_id: str) -> dict:

        state = conversation_state.get_state(user_id)
        current_function = state.get("current_function")
        collected_params = state.get("collected_params", {})
        missing_params = state.get("missing_params", [])
        try:

            if not current_function:
                intent = json.loads(classify_intent(user_input))
                function_name = intent.get("function")
                arguments = intent.get("arguments", {})

                if not function_name:
                    return {"status": "error", "message": "Could not determine intent."}

                conversation_state.update_state(user_id, function_name=function_name, collected_params=arguments)
                merged_params = conversation_state.merge_params(user_id, arguments)
                required_params = FUNCTION_REQUIRED_PARAMS.get(function_name, [])
                missing = [p for p in required_params if not merged_params.get(p)]
                if missing:
                    conversation_state.update_state(user_id, missing_params=missing)
                    return {
                        "status": "need_info",
                        "message": get_missing_params_message(function_name, missing),
                        "function": function_name,
                        "missing_params": missing,
                    }
                return self._run_function(function_name, merged_params, user_id)
                        
        except Exception as e:
            print("Error in process", str(e))
            return {"status": "error", "message": "Error in process"}


        required_params = FUNCTION_REQUIRED_PARAMS.get(current_function, [])
        if missing_params:
            extraction = extract_parameters(user_input, current_function, missing_params, collected_params)
            new_args = json.loads(extraction).get("arguments", {})
            merged_params = conversation_state.merge_params(user_id, new_args)
            conversation_state.update_state(user_id, collected_params=new_args)
            still_missing = [p for p in required_params if not merged_params.get(p)]
            if still_missing:
                conversation_state.update_state(user_id, missing_params=still_missing)
                return {
                    "status": "need_info",
                    "message": get_missing_params_message(current_function, still_missing),
                    "function": current_function,
                    "missing_params": still_missing,
                }
            return self._run_function(current_function, merged_params, user_id)

        return self.process(user_input, user_id)

    def _run_function(self, function_name: str, params: dict, user_id: str) -> dict:

        if function_name == "book_table":

            try:
                message = book_table(
                    user_id=user_id,
                    date=params.get("date"),
                    time=params.get("time"),
                    restaurant_location=params.get("restaurant_location"),
                    number_of_people=params.get("number_of_people"),
                )
                print("message", message)

            except Exception as e:
                print("Error in booking table")
                return {"status": "error", "message": "Error in booking table"}

            conversation_state.clear_state(user_id)
            return {"status": "ok", "message": message}

        return {"status": "error", "message": "Unknown function."}

agent_orchestrator = AgentOrchestrator()
