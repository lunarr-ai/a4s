import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/agent_model.dart';
import 'package:lunarr/services/agent_service.dart';

class AgentChatController {
  bool _lock = false;
  late List<List<AgentCardModel>> _agentCardModelss;
  final TextEditingController _textEditingController = TextEditingController();
  String input = '';

  bool get lock => _lock;
  List<List<AgentCardModel>> get agentCardModelss => _agentCardModelss;
  TextEditingController get textEditingController => _textEditingController;

  // TODO: integrate API (not for now)
  Future<void> fetchAgentCardModels() async {
    final AgentModel am = AgentService().agentModel;

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
    _lock = true;

    List<AgentCardModel> agentCardModels = [
      AgentCardModel.seungho(true),
      AgentCardModel.kyungho(true),
      AgentCardModel.minseok(true),
      AgentCardModel.seungho(true),
    ];

    _agentCardModelss.add(agentCardModels);
  }

  // TODO: integrate API using _agentCardModels
  Future<void> getAgentChatModel() async {
    _lock = false;
  }
}
