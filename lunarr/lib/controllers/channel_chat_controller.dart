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
  final ChannelService _channelService = ChannelService();
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
    final channel = _channelService.channelModel;

    if (channel.id.isEmpty) {
      _channelChatModels.add(ChannelChatModel.selectionExample());
      scroll();
      return;
    }

    final chatResponse = await _channelService.sendChannelMessage(
      channel.id,
      _input,
    );

    if (chatResponse == null) {
      _channelChatModels.add(ChannelChatModel.selectionExample());
      scroll();
      return;
    }

    if (chatResponse.type == ChannelChatResponseType.direct) {
      _addDirectAnswer(chatResponse.directResponse ?? '');
      return;
    }

    if (chatResponse.type == ChannelChatResponseType.candidates &&
        chatResponse.candidates != null &&
        chatResponse.candidates!.isNotEmpty) {
      final agentCards = chatResponse.candidates!
          .map(
            (c) => AgentCardModel(
              id: c.id,
              iconString: 'assets/avatars/1.png',
              name: c.name,
              distributionList: '',
              description: c.reason,
              instruction: '',
              model: '',
              tools: [],
              knowledges: [],
              isSelected: true,
            ),
          )
          .toList();

      _channelChatModels.add(ChannelChatModel.selection((body: agentCards)));
    } else {
      _channelChatModels.add(ChannelChatModel.selectionExample());
    }

    scroll();
  }

  void _addDirectAnswer(String response) {
    final agentCard = AgentCardModel(
      id: 'backbone',
      iconString: 'assets/avatars/1.png',
      name: 'Assistant',
      distributionList: '',
      description: '',
      instruction: '',
      model: '',
      tools: [],
      knowledges: [],
      isSelected: false,
    );

    _channelChatModels.add(
      ChannelChatModel.answers([(agentCardModel: agentCard, body: response)]),
    );
    scroll();
    _lock = false;
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
    final channel = _channelService.channelModel;

    if (channel.id.isNotEmpty && _selectedAgentIds.isNotEmpty) {
      final chatResponse = await _channelService.sendChannelMessage(
        channel.id,
        _input,
        agentIds: _selectedAgentIds,
      );

      if (chatResponse != null &&
          chatResponse.results != null &&
          chatResponse.results!.isNotEmpty) {
        final agentCards = chatResponse.results!
            .map(
              (r) => AgentCardModel(
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
              ),
            )
            .toList();

        final answerModels = chatResponse.results!
            .asMap()
            .entries
            .map(
              (entry) => (
                agentCardModel: agentCards[entry.key],
                body:
                    entry.value.response ?? entry.value.error ?? 'No response',
              ),
            )
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
