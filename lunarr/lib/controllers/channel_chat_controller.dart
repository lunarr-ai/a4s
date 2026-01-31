import 'package:lunarr/models/agent_card_model.dart';

class ChannelChatController {
  bool _lock = false;
  List<List<AgentCardModel>> _agentCardModelss = [
    [
      AgentCardModel.seungho(false),
      AgentCardModel.kyungho(true),
      AgentCardModel.minseok(true),
      AgentCardModel.seungho(true),
    ],
    [
      AgentCardModel.seungho(true),
      AgentCardModel.kyungho(false),
      AgentCardModel.minseok(true),
      AgentCardModel.seungho(true),
    ],
  ];

  bool get lock => _lock;
  List<List<AgentCardModel>> get agentCardModelss => _agentCardModelss;

  // TODO: integrate API
  Future<bool> getAgentCardModels() async {
    if (_lock) return false;
    _lock = true;

    List<AgentCardModel> _agentCardModels = [
      AgentCardModel.seungho(true),
      AgentCardModel.kyungho(true),
      AgentCardModel.minseok(true),
      AgentCardModel.seungho(true),
    ];

    _agentCardModelss.add(_agentCardModels);

    return true;
  }

  // TODO: integrate API using _agentCardModels
  Future<bool> getChannelChatModel() async {
    _lock = false;
    return true;
  }
}
