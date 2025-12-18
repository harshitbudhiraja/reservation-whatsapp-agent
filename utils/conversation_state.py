class ConversationState:
    def __init__(self):
        self.states = {}
    
    def get_state(self, user_id):
        return self.states.get(user_id, {
            "current_function": None,
            "collected_params": {},
            "missing_params": []
        })
    
    def update_state(self, user_id, function_name=None, collected_params=None, missing_params=None):
        if user_id not in self.states:
            self.states[user_id] = {
                "current_function": None,
                "collected_params": {},
                "missing_params": []
            }
        
        if function_name is not None:
            self.states[user_id]["current_function"] = function_name
        
        if collected_params is not None:
            self.states[user_id]["collected_params"].update(collected_params)
        
        if missing_params is not None:
            self.states[user_id]["missing_params"] = missing_params
    
    def clear_state(self, user_id):
        if user_id in self.states:
            del self.states[user_id]
    
    def merge_params(self, user_id, new_params):
        state = self.get_state(user_id)
        merged = state["collected_params"].copy()
        for key, value in new_params.items():
            if value is not None and value != "":
                merged[key] = value
        return merged

conversation_state = ConversationState()

