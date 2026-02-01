import 'package:flutter/material.dart';
import 'package:lunarr/controllers/channel_chat_controller.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/channel_chat_model.dart';
import 'package:lunarr/models/channel_model.dart';
import 'package:lunarr/models/chat_model.dart';
import 'package:lunarr/services/channel_service.dart';
import 'package:lunarr/widgets/agent_card_widget.dart';

class ChannelChatView extends StatefulWidget {
  const ChannelChatView({super.key});

  @override
  State<ChannelChatView> createState() => _ChannelChatViewState();
}

class _ChannelChatViewState extends State<ChannelChatView> {
  final ChannelChatController ccc = ChannelChatController();

  late Future<void> initFuture;

  @override
  void initState() {
    super.initState();
    initFuture = ccc.fetchChannelChatModels();
  }

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;

    return Stack(
      children: [
        Column(children: [_buildAppBar(tt, cs), _buildChat(cs, tt)]),
        _buildGradient(cs),
        _buildInput(cs, tt),
      ],
    );
  }

  Expanded _buildChat(ColorScheme cs, TextTheme tt) {
    return Expanded(
      child: FutureBuilder(
        future: initFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator());
          }
          return SingleChildScrollView(
            controller: ccc.scrollController,
            padding: EdgeInsets.only(bottom: 212, top: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              spacing: 24,
              children: [
                ...ccc.channelChatModels.map((ccms) {
                  switch (ccms.type) {
                    case ChannelChatType.question:
                      return _buildQuestion(ccms.questionModel!, cs, tt);
                    case ChannelChatType.selection:
                      return _buildSelection(
                        ccms.selectionModel!,
                        cs,
                        tt,
                        ccc.lock && ccms == ccc.channelChatModels.last,
                      );
                    case ChannelChatType.thinkings:
                      return _buildThinkings(ccms.thinkingModels!, cs, tt);
                    case ChannelChatType.answers:
                      return _buildAnswers(ccms.answerModels!, cs, tt);
                  }
                }),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildQuestion(QuestionModel qm, ColorScheme cs, TextTheme tt) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          constraints: BoxConstraints(maxWidth: 720),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Container(
                constraints: BoxConstraints(maxWidth: 480),
                padding: EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: cs.surface,
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(24),
                    bottomLeft: Radius.circular(24),
                    bottomRight: Radius.circular(24),
                  ),
                ),
                child: Text(
                  qm.body,
                  style: tt.bodyLarge?.copyWith(color: cs.onSurface),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSelection(
    SelectionModel sm,
    ColorScheme cs,
    TextTheme tt,
    bool enabled,
  ) {
    List<AgentCardModel> acms = sm.body;

    if (enabled) {
      final ValueNotifier<int> areSelectedCount = ValueNotifier<int>(0);

      void updateAreSelectedCount() {
        areSelectedCount.value = acms.where((e) => e.isSelected).length;
      }

      void deleteAreSelectedCount() {
        areSelectedCount.dispose();
      }

      updateAreSelectedCount();

      final ValueNotifier<bool> isConfirmed = ValueNotifier<bool>(false);

      void updateIsConfirmed() {
        isConfirmed.value = !isConfirmed.value;
      }

      void deleteIsConfirmed() {
        isConfirmed.dispose();
      }

      return Column(
        spacing: 24,
        children: [
          Container(
            constraints: const BoxConstraints(maxWidth: 720),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                ValueListenableBuilder<int>(
                  valueListenable: areSelectedCount,
                  builder: (context, count, child) {
                    return Text(
                      '$count Agents Selected',
                      style: tt.titleLarge?.copyWith(color: cs.onSurface),
                    );
                  },
                ),
                ValueListenableBuilder<bool>(
                  valueListenable: isConfirmed,
                  builder: (context, value, child) {
                    return FilledButton(
                      onPressed: isConfirmed.value
                          ? null
                          : () async {
                              updateIsConfirmed();
                              deleteAreSelectedCount();
                              deleteIsConfirmed();

                              await ccc.addThinkings();
                              setState(() {});

                              await ccc.addAnswer();
                              setState(() {});
                            },
                      child: Text('Confirm'),
                    );
                  },
                ),
              ],
            ),
          ),
          Column(
            spacing: 8,
            children: [
              for (int i = 0; i < acms.length; i += 2)
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  spacing: 8,
                  children: [
                    ValueListenableBuilder<bool>(
                      valueListenable: isConfirmed,
                      builder: (context, value, child) {
                        return AgentCardWidget(
                          acm: acms[i],
                          onTap: isConfirmed.value
                              ? null
                              : () {
                                  updateAreSelectedCount();
                                },
                        );
                      },
                    ),
                    if (i + 1 < acms.length) ...[
                      ValueListenableBuilder<bool>(
                        valueListenable: isConfirmed,
                        builder: (context, value, child) {
                          return AgentCardWidget(
                            acm: acms[i + 1],
                            onTap: isConfirmed.value
                                ? null
                                : () {
                                    updateAreSelectedCount();
                                  },
                          );
                        },
                      ),
                    ],
                  ],
                ),
            ],
          ),
        ],
      );
    } else {
      return Column(
        spacing: 24,
        children: [
          Container(
            constraints: const BoxConstraints(maxWidth: 720),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${acms.where((e) => e.isSelected).length} Agents Selected',
                  style: tt.titleLarge?.copyWith(color: cs.onSurface),
                ),
                FilledButton(onPressed: null, child: Text('Confirm')),
              ],
            ),
          ),
          Column(
            spacing: 8,
            children: [
              for (int i = 0; i < acms.length; i += 2)
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  spacing: 8,
                  children: [
                    AgentCardWidget(acm: acms[i]),
                    if (i + 1 < acms.length) ...[
                      AgentCardWidget(acm: acms[i + 1]),
                    ],
                  ],
                ),
            ],
          ),
        ],
      );
    }
  }

  Widget _buildThinkings(
    List<ThinkingModel> tms,
    ColorScheme cs,
    TextTheme tt,
  ) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          constraints: BoxConstraints(maxWidth: 720),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                constraints: BoxConstraints(maxWidth: 480),
                padding: EdgeInsets.symmetric(horizontal: 24),
                child: Row(
                  spacing: 12,
                  children: [
                    ...tms.map(
                      (tm) => CircleAvatar(
                        radius: 12,
                        child: Image.asset(tm.agentCardModel.iconString),
                      ),
                    ),
                    Text(
                      'Show Thinking',
                      style: tt.labelLarge?.copyWith(
                        color: cs.onSurface,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    IconButton(
                      onPressed: () {},
                      icon: Icon(Icons.arrow_drop_down),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildAnswers(List<AnswerModel> ams, ColorScheme cs, TextTheme tt) {
    final ChannelModel cm = ChannelService().channelModel;

    return Column(
      spacing: 24,
      children: ams.map((am) {
        return Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              constraints: BoxConstraints(maxWidth: 720),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    constraints: BoxConstraints(maxWidth: 480),
                    padding: EdgeInsets.symmetric(horizontal: 24),
                    child: Column(
                      spacing: 12,
                      children: [
                        Row(
                          spacing: 12,
                          children: [
                            CircleAvatar(
                              radius: 12,
                              child: Image.asset(am.agentCardModel.iconString),
                            ),
                            Text(
                              am.agentCardModel.name,
                              style: tt.labelLarge?.copyWith(
                                color: cs.onSurface,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        Text(
                          am.body,
                          style: tt.bodyLarge?.copyWith(color: cs.onSurface),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        );
      }).toList(),
    );
  }

  Widget _buildGradient(ColorScheme cs) {
    return Align(
      alignment: Alignment.bottomCenter,
      child: Container(
        height: 320,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.white.withAlpha(0), Colors.white, Colors.white],
            stops: [0.0, 0.75, 1.0],
          ),
        ),
      ),
    );
  }

  Widget _buildInput(ColorScheme cs, TextTheme tt) {
    final ChannelModel cm = ChannelService().channelModel;
    return Align(
      alignment: Alignment.bottomCenter,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          spacing: 12,
          children: [
            Card.outlined(
              color: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(28),
                side: BorderSide(color: cs.outline),
              ),
              child: Container(
                constraints: const BoxConstraints(maxWidth: 720),
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 16,
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextField(
                      onSubmitted: ccc.lock
                          ? null
                          : (_) async {
                              ccc.addQuestion();
                              setState(() {});

                              await ccc.addSelection();
                              setState(() {});
                            },
                      enabled: !ccc.lock,
                      controller: ccc.textEditingController,
                      onChanged: (value) {
                        ccc.input = value;
                      },
                      decoration: InputDecoration(
                        hintText: 'Ask ${cm.labelString}',
                        hintStyle: tt.bodyLarge?.copyWith(
                          color: cs.onSurfaceVariant,
                        ),
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.zero,
                      ),
                      style: tt.bodyLarge?.copyWith(color: cs.onSurface),
                    ),
                    SizedBox(
                      height: 48,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              IconButton(
                                onPressed: () {},
                                icon: Icon(Icons.add, color: cs.onSurface),
                              ),
                              TextButton.icon(
                                onPressed: () {},
                                icon: Icon(Icons.tune, color: cs.onSurface),
                                label: Text(
                                  'Tools',
                                  style: tt.labelLarge?.copyWith(
                                    color: cs.onSurface,
                                  ),
                                ),
                                style: TextButton.styleFrom(
                                  foregroundColor: cs.onSurface,
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          IconButton(
                            onPressed: ccc.lock
                                ? null
                                : () async {
                                    ccc.addQuestion();
                                    setState(() {});

                                    await ccc.addSelection();
                                    setState(() {});
                                  },
                            icon: Icon(
                              ccc.lock ? Icons.stop : Icons.send,
                              color: cs.onSurface,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Text(
              'Lunarr can make mistakes, including about people, so double-check it.',
              style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppBar(TextTheme tt, ColorScheme cs) {
    final ChannelModel cm = ChannelService().channelModel;
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 12, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            spacing: 12,
            children: [
              cm.getIcon(16),
              Text(
                cm.labelString,
                style: tt.titleLarge?.copyWith(color: cs.onSurface),
              ),
            ],
          ),
          Row(
            children: [
              TextButton.icon(
                icon: Icon(Icons.person, color: cs.onSurface),
                onPressed: () {},
                label: Text(
                  '${cm.agentsCount}',
                  style: tt.labelLarge?.copyWith(color: cs.onSurface),
                ),
              ),
              IconButton(
                onPressed: () {},
                icon: Icon(Icons.more_vert, color: cs.onSurface),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
