import 'dart:async';

import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/channel_chat_model.dart';

class ChannelChatController {
  bool _lock = false;
  final List<ChannelChatModel> _channelChatModels = [];
  final TextEditingController _textEditingController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  String input = '';
  String _input = '';

  bool get lock => _lock;
  List<ChannelChatModel> get channelChatModels => _channelChatModels;
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
  Future<void> fetchChannelChatModels() async {
    await Future.delayed(const Duration(seconds: 1));
    List<ChannelChatModel> channelChatModels = [
      for (int i = 0; i < 4; i++)
        ...ChannelChatModel.examples([
          AgentCardModel.kyungho(false),
          AgentCardModel.minseok(false),
          AgentCardModel.seungho(false),
        ]),
    ];

    _channelChatModels.addAll(channelChatModels);
    scroll();
  }

  void addQuestion() {
    if (input.isEmpty) return;
    _lock = true;

    _input = input;
    input = '';
    _textEditingController.clear();

    _channelChatModels.add(ChannelChatModel.question((body: _input)));
    scroll();
  }

  // TODO: integrate API
  Future<void> addSelection() async {
    await Future.delayed(const Duration(seconds: 1));
    ChannelChatModel selection = ChannelChatModel.selectionExample();

    _channelChatModels.add(selection);
    scroll();
  }

  // TODO: integrate API (not for now)
  Future<void> addThinkings() async {
    List<AgentCardModel> agentCardModels = [
      AgentCardModel.kyungho(false),
      AgentCardModel.minseok(false),
      AgentCardModel.seungho(false),
    ];

    await Future.delayed(const Duration(seconds: 1));
    ChannelChatModel thinking = ChannelChatModel.thinkingsExample(
      agentCardModels,
    );

    _channelChatModels.add(thinking);
    scroll();
  }

  // TODO: integrate API
  Future<void> addAnswer() async {
    List<AgentCardModel> agentCardModels = [
      AgentCardModel.kyungho(false),
      AgentCardModel.minseok(false),
      AgentCardModel.seungho(false),
    ];

    await Future.delayed(const Duration(seconds: 1));
    ChannelChatModel answer = ChannelChatModel.answersExample(agentCardModels);

    _channelChatModels.add(answer);
    scroll();

    _lock = false;
  }
}
