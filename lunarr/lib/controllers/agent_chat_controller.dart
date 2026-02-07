import 'dart:async';

import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/agent_chat_model.dart';
import 'package:lunarr/services/agent_service.dart';

class AgentChatController {
  bool _lock = false;
  final List<AgentChatModel> _agentChatModels = [];
  final TextEditingController _textEditingController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  String input = '';
  String _input = '';
  String? _selectedAgentId;

  bool get lock => _lock;
  List<AgentChatModel> get agentChatModels => _agentChatModels;
  TextEditingController get textEditingController => _textEditingController;
  ScrollController get scrollController => _scrollController;

  void scroll() {
    Timer(const Duration(milliseconds: 300), () {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  // TODO: integrate API (not for now)
  Future<void> fetchAgentChatModels() async {
    AgentCardModel agentCardModel = AgentCardModel.seungho(false);

    await Future.delayed(const Duration(seconds: 1));
    List<AgentChatModel> agentChatModels = [
      for (int i = 0; i < 4; i++) ...AgentChatModel.examples(agentCardModel),
    ];

    _agentChatModels.addAll(agentChatModels);
    scroll();
  }

  void addQuestion() {
    if (input.isEmpty) return;
    _lock = true;

    _input = input;
    input = '';
    _textEditingController.clear();

    _agentChatModels.add(AgentChatModel.question((body: _input)));
    scroll();
  }

  Future<void> addSelection() async {
    final agentService = AgentService();

    var agents = await agentService.searchAgents(_input);
    if (agents.isEmpty) {
      agents = agentService.agents;
    }

    List<AgentCardModel> agentCards;
    if (agents.isNotEmpty) {
      agentCards = agents
          .asMap()
          .entries
          .map(
            (e) => AgentCardModel.fromAgent(
              e.value,
              isSelected: e.key == 0,
              avatarIndex: (e.key % 30) + 1,
            ),
          )
          .toList();
      _selectedAgentId = agents.first.id;
    } else {
      agentCards = [
        AgentCardModel.seungho(true),
        AgentCardModel.kyungho(false),
        AgentCardModel.minseok(false),
      ];
    }

    _agentChatModels.add(AgentChatModel.selection((body: agentCards)));
    scroll();
  }

  // TODO: integrate API (not for now)
  Future<void> addThinking() async {
    AgentCardModel agentCardModel = AgentCardModel.seungho(false);

    await Future.delayed(const Duration(seconds: 1));
    AgentChatModel thinking = AgentChatModel.thinkingExample(agentCardModel);

    _agentChatModels.add(thinking);
    scroll();
  }

  Future<void> addAnswer() async {
    final agentService = AgentService();

    AgentCardModel agentCardModel;
    String? responseText;

    if (_selectedAgentId != null) {
      final agent = agentService.getAgentById(_selectedAgentId!);
      if (agent != null) {
        agentCardModel = AgentCardModel.fromAgent(agent, isSelected: false);
        responseText = await agentService.sendMessage(
          _selectedAgentId!,
          _input,
        );
      } else {
        agentCardModel = AgentCardModel.seungho(false);
      }
    } else {
      agentCardModel = AgentCardModel.seungho(false);
    }

    final answerBody = responseText ?? 'Unable to get response from agent.';
    final answer = AgentChatModel.answer((
      agentCardModel: agentCardModel,
      body: answerBody,
    ));

    _agentChatModels.add(answer);
    scroll();

    _lock = false;
  }
}
