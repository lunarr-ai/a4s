import 'package:lunarr/models/agent_card_model.dart';

class AgentChatController {
  bool _lock = false;
  late List<List<AgentCardModel>> _agentCardModelss;

  bool get lock => _lock;
  List<List<AgentCardModel>> get agentCardModelss => _agentCardModelss;

  // TODO: integrate API (not for now)
  Future<void> fetchAgentCardModels() async {
    _agentCardModelss = [
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
  }

  // TODO: integrate API
  Future<void> getAgentCardModels() async {
    if (_lock) return;

    List<AgentCardModel> _agentCardModels = [
      AgentCardModel.seungho(true),
      AgentCardModel.kyungho(true),
      AgentCardModel.minseok(true),
      AgentCardModel.seungho(true),
    ];

    _agentCardModelss.add(_agentCardModels);
  }

  // TODO: integrate API using _agentCardModels
  Future<void> getAgentChatModel() async {
    _lock = false;
  }
}
