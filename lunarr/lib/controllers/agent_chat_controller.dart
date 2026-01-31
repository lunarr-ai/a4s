import 'package:lunarr/models/agent_card_model.dart';

class AgentChatController {
  // TODO: integrate API
  Future<List<AgentCardModel>> getAgentCardModels() async {
    return [
      AgentCardModel.seungho(true),
      AgentCardModel.kyungho(true),
      AgentCardModel.minseok(true),
      AgentCardModel.seungho(true),
    ];
  }
}
