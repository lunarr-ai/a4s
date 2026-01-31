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
  final AgentModel am = AgentService().agentModel;
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
          children: [
            _buildAppBar(am, tt, cs),
            Expanded(
              child: FutureBuilder(
                future: initFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return Center(child: CircularProgressIndicator());
                  }
                  return SingleChildScrollView(
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
            ),
          ],
        ),
        IconButton(
          onPressed: acc.lock
              ? null
              : () async {
                  await acc.getAgentCardModels();
                  setState(() {});
                },
          icon: Icon(Icons.send, color: cs.onSurface),
        ),
      ],
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
          SizedBox(
            width: 720,
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
                          : () {
                              updateIsConfirmed();
                              deleteAreSelectedCount();
                              deleteIsConfirmed();
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
          SizedBox(
            width: 720,
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

  Widget _buildAppBar(AgentModel agentModel, TextTheme tt, ColorScheme cs) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 12, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            spacing: 12,
            children: [
              agentModel.getIcon(16),
              Text(
                agentModel.labelString,
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
