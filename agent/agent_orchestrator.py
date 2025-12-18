from prompts.intent_classify import classify_intent
from prompts.parameter_extractor import extract_parameters
from utils.conversation_state import conversation_state
from utils.message_templates import FUNCTION_REQUIRED_PARAMS, get_missing_params_message

class AgentOrchestrator:
    def __init__(self):
        self.intent_classifier = classify_intent
        self.parameter_extractor = extract_parameters
    
    def process(self, user_input: str, user_id: str) -> dict:
        state = conversation_state.get_state(user_id)
        current_function = state["current_function"]
        collected_params = state["collected_params"]
        missing_params = state["missing_params"]
        
        if not current_function:
            return self._handle_intent_classification(user_input, user_id)
        else:
            intent_check = self.intent_classifier(user_input)
            import json
            intent_json = json.loads(intent_check)
            new_function = intent_json.get("function")
            
            if new_function and new_function != current_function:
                conversation_state.clear_state(user_id)
                return self._handle_intent_classification(user_input, user_id)
            
            return self._handle_parameter_extraction(user_input, user_id, current_function, missing_params, collected_params)
    
    def _handle_intent_classification(self, user_input: str, user_id: str) -> dict:
        intent_result = self.intent_classifier(user_input)
        import json
        intent_json = json.loads(intent_result)
        function_name = intent_json.get("function")
        initial_arguments = intent_json.get("arguments", {})
        
        if not function_name:
            return {
                "status": "error",
                "message": "Could not classify intent or no matching function.",
            }
        
        conversation_state.update_state(user_id, function_name=function_name, collected_params=initial_arguments)
        merged_params = conversation_state.merge_params(user_id, initial_arguments)
        
        required_params = FUNCTION_REQUIRED_PARAMS.get(function_name, [])
        missing_params = [param for param in required_params if not merged_params.get(param) or merged_params.get(param) == ""]
        
        if missing_params:
            question_message = get_missing_params_message(function_name, missing_params)
            conversation_state.update_state(user_id, missing_params=missing_params)
            return {"status": "need_info", "message": question_message, "function": function_name, "missing_params": missing_params}
        
        return self._execute_function(function_name, merged_params, user_id)
    
    def _handle_parameter_extraction(self, user_input: str, user_id: str, function_name: str, missing_params: list, collected_params: dict) -> dict:
        if not missing_params:
            return self._handle_intent_classification(user_input, user_id)
        
        param_result = self.parameter_extractor(user_input, function_name, missing_params, collected_params)
        import json
        param_json = json.loads(param_result)
        extracted_arguments = param_json.get("arguments", {})
        
        merged_params = conversation_state.merge_params(user_id, extracted_arguments)
        conversation_state.update_state(user_id, collected_params=extracted_arguments)
        
        required_params = FUNCTION_REQUIRED_PARAMS.get(function_name, [])
        still_missing = [param for param in required_params if not merged_params.get(param) or merged_params.get(param) == ""]
        
        if still_missing:
            question_message = get_missing_params_message(function_name, still_missing)
            conversation_state.update_state(user_id, missing_params=still_missing)
            return {"status": "need_info", "message": question_message, "function": function_name, "missing_params": still_missing}
        
        return self._execute_function(function_name, merged_params, user_id)
    
    def _execute_function(self, function_name: str, params: dict, user_id: str) -> dict:
        from agent.mcp_server import book_table, get_table_status, get_menu_details
        
        if function_name == "book_table":
            message = book_table(
                date=params.get("date"),
                time=params.get("time"),
                restaurant_location=params.get("restaurant_location"),
                number_of_people=params.get("number_of_people"),
            )
            conversation_state.clear_state(user_id)
            return {"status": "ok", "message": message}

        elif function_name == "get_table_status":
            message = get_table_status(
                table_id=params.get("table_id"),
                restaurant_location=params.get("restaurant_location"),
            )
            conversation_state.clear_state(user_id)
            return {"status": "ok", "message": message}

        elif function_name == "get_menu_details":
            message = get_menu_details(
                restaurant_location=params.get("restaurant_location"),
            )
            conversation_state.clear_state(user_id)
            return {"status": "ok", "message": message}
        
        return {
            "status": "error",
            "message": "Unknown function.",
        }

agent_orchestrator = AgentOrchestrator()

