import 'package:flutter/material.dart';
import 'package:lunarr/controllers/agent_chat_controller.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/agent_model.dart';
import 'package:lunarr/services/agent_service.dart';
import 'package:lunarr/widgets/agent_card_widget.dart';

class AgentChatView extends StatefulWidget {
  const AgentChatView({super.key});

  @override
  State<AgentChatView> createState() => _AgentChatViewState();
}

class _AgentChatViewState extends State<AgentChatView> {
  final AgentChatController acc = AgentChatController();

  late Future<void> initFuture;

  @override
  void initState() {
    super.initState();
    initFuture = acc.fetchAgentCardModels();
  }

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;

    return Stack(
      children: [
        Column(
          spacing: 24,
          children: [_buildAppBar(tt, cs), _buildChat(cs, tt)],
        ),
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
            padding: const EdgeInsets.only(bottom: 200),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              spacing: 24,
              children: [
                ...acc.agentCardModelss.map(
                  (acms) => _buildAgentCards(
                    acms,
                    cs,
                    tt,
                    acc.lock && acms == acc.agentCardModelss.last,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildGradient(ColorScheme cs) {
    return Align(
      alignment: Alignment.bottomCenter,
      child: Container(
        height: 300,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.white.withAlpha(0), Colors.white, Colors.white],
            stops: const [0.0, 0.8, 1.0],
          ),
        ),
      ),
    );
  }

  Widget _buildInput(ColorScheme cs, TextTheme tt) {
    final AgentModel am = AgentService().agentModel;
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
                      controller: acc.textEditingController,
                      onChanged: (value) {
                        acc.input = value;
                      },
                      decoration: InputDecoration(
                        hintText: 'Ask ${am.labelString}',
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
                                    // TODO
                                    await acc.getAgentCardModels();
                                    setState(() {});
                                  },
                            icon: Icon(Icons.send, color: cs.onSurface),
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

  Widget _buildAgentCards(
    List<AgentCardModel> acms,
    ColorScheme cs,
    TextTheme tt,
    bool enabled,
  ) {
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

                              await acc.getAgentChatModel();
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

  Widget _buildAppBar(TextTheme tt, ColorScheme cs) {
    final AgentModel am = AgentService().agentModel;
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 12, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            spacing: 12,
            children: [
              am.getIcon(16),
              Text(
                am.labelString,
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
