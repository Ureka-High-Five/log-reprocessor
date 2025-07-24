from app.enum.action_type import ActionType

def convert_to_weight(type : ActionType, value : float) -> float :
  if type == ActionType.CLICK:
    return 0.2
  if type == ActionType.LIKE:
    return 0.1
  if type == ActionType.WATCH:
    if 30 <= value <= 50:
      return 0.1
    if 50 <= value <= 70:
      return 0.2
    if 70 <= value:
      return 0.3
    else:
      return 0
  if type == ActionType.RATING:
    if value <= 2:
      return 0
    if value == 3:
      return 0.2
    if value == 4:
      return 0.3
    if value == 5:
      return 0.4
