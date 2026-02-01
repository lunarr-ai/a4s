import 'package:lunarr/models/agent_card_model.dart';

typedef QuestionModel = ({String body});
typedef SelectionModel = ({List<AgentCardModel> body});
typedef ThinkingModel = ({AgentCardModel agentCardModel, Object? body});
typedef AnswerModel = ({AgentCardModel agentCardModel, String body});
