

class SkillService:
    def __init__(self, game_state):
        self.game_state = game_state

    def get_skill(self, skill_id):
        return self.game_state.skills.get(skill_id)

    def add_skill(self, skill):
        self.game_state.skills[skill.id] = skill

    def remove_skill(self, skill_id):
        if skill_id in self.game_state.skills:
            del self.game_state.skills[skill_id]