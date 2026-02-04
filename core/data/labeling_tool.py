# This is a placeholder for a potential UI-based or script-based labeling tool.
# For now, it contains functions that might be used in such a tool.

from typing import Dict, Any

def assign_behavior_label(event: Dict[str, Any]) -> str:
    """
    Assigns a behavioral label based on event content.
    This would be replaced by manual annotation in a real tool.
    """
    content = event.get('content', '').lower()
    if 'attack' in content or 'suspicious' in content:
        return 'aggressive'
    elif 'defend' in content or 'trust' in content:
        return 'defensive'
    elif 'check' in content or 'seer' in content:
        return 'investigative'
    else:
        return 'neutral'

def assign_wolf_label(player_id: str, wolf_list: list) -> int:
    """
    Assigns a label indicating if a player is a wolf.
    """
    return 1 if player_id in wolf_list else 0


if __name__ == '__main__':
    print("Labeling tool module created.")
    # Example usage:
    # event_example = {'content': 'I think player2 is very suspicious.'}
    # behavior = assign_behavior_label(event_example)
    # print(f"Behavior label: {behavior}")
    #
    # wolf_label = assign_wolf_label('player2', ['player2', 'player4'])
    # print(f"Is wolf: {wolf_label}")
