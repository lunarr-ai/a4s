import 'dart:async';

import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/channel_model.dart';
import 'package:lunarr/services/channel_service.dart';

class ChannelChatController {
  bool _lock = false;
  late List<List<AgentCardModel>> _agentCardModelss;
  final TextEditingController _textEditingController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  String _input = '';

  bool get lock => _lock;
  List<List<AgentCardModel>> get agentCardModelss => _agentCardModelss;
  TextEditingController get textEditingController => _textEditingController;
  ScrollController get scrollController => _scrollController;
  String get input => _input;

  set input(String value) {
    _input = value;
  }

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
  Future<void> fetchAgentCardModels() async {
    final ChannelModel cm = ChannelService().channelModel;

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
    if (_lock || input.isEmpty) return;
    _lock = true;

    List<AgentCardModel> agentCardModels = [
      AgentCardModel.seungho(true),
      AgentCardModel.kyungho(true),
      AgentCardModel.minseok(true),
      AgentCardModel.seungho(true),
    ];

    _agentCardModelss.add(agentCardModels);

    _input = '';
    _textEditingController.clear();
    scroll();
  }

  // TODO: integrate API using _agentCardModels
  Future<void> getChannelChatModel() async {
    scroll();

    _lock = false;
  }
}
