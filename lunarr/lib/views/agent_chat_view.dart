import 'package:flutter/material.dart';
import 'package:lunarr/controllers/agent_chat_controller.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/agent_chat_model.dart';
import 'package:lunarr/models/chat_model.dart';
import 'package:lunarr/services/agent_card_service.dart';

class AgentChatView extends StatefulWidget {
  final String agentId;

  const AgentChatView({super.key, required this.agentId});

  @override
  State<AgentChatView> createState() => _AgentChatViewState();
}

class _AgentChatViewState extends State<AgentChatView> {
  late final AgentChatController acc = AgentChatController(
    agentId: widget.agentId,
  );

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
      child: SingleChildScrollView(
        controller: acc.scrollController,
        padding: EdgeInsets.only(bottom: 212, top: 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          spacing: 24,
          children: [
            ...acc.agentChatModels.map((acms) {
              switch (acms.type) {
                case AgentChatType.question:
                  return _buildQuestion(acms.questionModel!, cs, tt);
                case AgentChatType.thinking:
                  return _buildThinking(acms.thinkingModel!, cs, tt);
                case AgentChatType.answer:
                  return _buildAnswer(acms.answerModel!, cs, tt);
              }
            }),
          ],
        ),
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

  Widget _buildThinking(ThinkingModel tm, ColorScheme cs, TextTheme tt) {
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
                    tm.agentCardModel.getIcon(12),
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

  Widget _buildAnswer(AnswerModel am, ColorScheme cs, TextTheme tt) {
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
                child: Text(
                  am.body,
                  style: tt.bodyLarge?.copyWith(color: cs.onSurface),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildGradient(ColorScheme cs) {
    return IgnorePointer(
      child: Align(
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
      ),
    );
  }

  Widget _buildInput(ColorScheme cs, TextTheme tt) {
    final AgentCardModel acm = AgentCardService().agentCardModel;
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
                      onSubmitted: acc.lock
                          ? null
                          : (_) async {
                              acc.addQuestion();
                              setState(() {});

                              await acc.addAnswer();
                              setState(() {});
                            },
                      enabled: !acc.lock,
                      controller: acc.textEditingController,
                      onChanged: (value) {
                        acc.input = value;
                      },
                      decoration: InputDecoration(
                        hintText: 'Ask ${acm.name}',
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
                            onPressed: acc.lock
                                ? null
                                : () async {
                                    acc.addQuestion();
                                    setState(() {});

                                    await acc.addAnswer();
                                    setState(() {});
                                  },
                            icon: Icon(
                              acc.lock ? Icons.stop : Icons.send,
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
    final AgentCardModel acm = AgentCardService().agentCardModel;
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 12, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            spacing: 12,
            children: [
              acm.getIcon(16),
              Text(
                acm.name,
                style: tt.titleLarge?.copyWith(color: cs.onSurface),
              ),
            ],
          ),
          Row(
            children: [
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
