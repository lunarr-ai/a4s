import 'dart:async';

import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/agent_chat_model.dart';
import 'package:lunarr/services/agent_card_service.dart';

class AgentChatController {
  bool _lock = false;
  final List<AgentChatModel> _agentChatModels = [];
  final TextEditingController _textEditingController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final AgentCardService _agentCardService = AgentCardService();

  String input = '';
  String _input = '';

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

  // TODO
  Future<void> fetchAgentChatModels() async {
    await Future.delayed(const Duration(seconds: 1));

    // AgentCardModel agentCardModel = AgentCardModel.seungho(false);
    // List<AgentChatModel> agentChatModels = [
    //   for (int i = 0; i < 4; i++) ...AgentChatModel.examples(agentCardModel),
    // ];
    // _agentChatModels.addAll(agentChatModels);

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

  // TODO
  Future<void> addThinking() async {
    await Future.delayed(const Duration(seconds: 1));

    AgentCardModel acm = _agentCardService.agentCardModel;
    AgentChatModel thinking = AgentChatModel.thinking((
      agentCardModel: acm,
      body: '',
    ));

    _agentChatModels.add(thinking);
    scroll();
  }

  Future<void> addAnswer() async {
    AgentCardModel acm = _agentCardService.agentCardModel;

    _agentChatModels.add(
      AgentChatModel.answer((
        agentCardModel: acm,
        body:
            await _agentCardService.sendMessage(acm.id, _getHistory()) ??
            'Unable to get response from agent.',
      )),
    );
    scroll();

    _lock = false;
  }

  String _getHistory() {
    return _agentChatModels
        .map(
          (acm) => switch (acm.type) {
            AgentChatType.question => 'User: ${acm.questionModel!.body}',
            AgentChatType.thinking => 'Thinking: ${acm.thinkingModel!.body}',
            AgentChatType.answer => 'Assistant: ${acm.answerModel!.body}',
          },
        )
        .join('\n');
  }
}
