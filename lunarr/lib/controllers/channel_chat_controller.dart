import 'dart:async';

import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/channel_chat_model.dart';
import 'package:lunarr/models/channel_model.dart';
import 'package:lunarr/services/channel_service.dart';

class ChannelChatController {
  bool _lock = false;
  final List<ChannelChatModel> _channelChatModels = [];
  final TextEditingController _textEditingController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  String input = '';
  String _input = '';
  List<String> _selectedAgentIds = [];

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

  Future<void> addSelection() async {
    final channelService = ChannelService();
    final channel = channelService.channelModel;

    List<AgentSummary> relevantAgents = [];

    if (channel.id.isNotEmpty) {
      relevantAgents =
          await channelService.searchRelevantAgents(channel.id, _input);
    }

    if (relevantAgents.isEmpty) {
      ChannelChatModel selection = ChannelChatModel.selectionExample();
      _channelChatModels.add(selection);
    } else {
      final agentCards = relevantAgents
          .map((a) => AgentCardModel(
                id: a.id,
                iconString: 'assets/avatars/1.png',
                name: a.name,
                distributionList: '',
                description: a.description,
                instruction: '',
                model: '',
                tools: [],
                knowledges: [],
                isSelected: true,
              ))
          .toList();

      _channelChatModels.add(ChannelChatModel.selection((body: agentCards)));
    }

    scroll();
  }

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

  void setSelectedAgentIds(List<String> agentIds) {
    _selectedAgentIds = agentIds;
  }

  Future<void> addAnswer() async {
    final channelService = ChannelService();
    final channel = channelService.channelModel;

    if (channel.id.isNotEmpty && _selectedAgentIds.isNotEmpty) {
      final chatResponse = await channelService.sendChannelMessage(
        channel.id,
        _input,
        _selectedAgentIds,
      );

      if (chatResponse != null && chatResponse.results.isNotEmpty) {
        final agentCards = chatResponse.results
            .map((r) => AgentCardModel(
                  id: r.agentId,
                  iconString: 'assets/avatars/1.png',
                  name: r.agentName,
                  distributionList: '',
                  description: '',
                  instruction: '',
                  model: '',
                  tools: [],
                  knowledges: [],
                  isSelected: false,
                ))
            .toList();

        final answerModels = chatResponse.results
            .asMap()
            .entries
            .map((entry) => (
                  agentCardModel: agentCards[entry.key],
                  body: entry.value.response ?? entry.value.error ?? 'No response',
                ))
            .toList();

        _channelChatModels.add(ChannelChatModel.answers(answerModels));
        scroll();
        _lock = false;
        _selectedAgentIds = [];
        return;
      }
    }

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
    _selectedAgentIds = [];
  }
}
