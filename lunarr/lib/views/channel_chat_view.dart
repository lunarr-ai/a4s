import 'package:flutter/material.dart';
import 'package:lunarr/controllers/channel_chat_controller.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/channel_model.dart';
import 'package:lunarr/services/channel_service.dart';
import 'package:lunarr/widgets/agent_card_widget.dart';

class ChannelChatView extends StatefulWidget {
  const ChannelChatView({super.key});

  @override
  State<ChannelChatView> createState() => _ChannelChatViewState();
}

class _ChannelChatViewState extends State<ChannelChatView> {
  final ChannelModel cm = ChannelService().channelModel;
  final ChannelChatController ccc = ChannelChatController();

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;

    return Stack(
      children: [
        Column(
          spacing: 24,
          children: [
            _buildAppBar(cm, tt, cs),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  spacing: 24,
                  children: [
                    ...ccc.agentCardModelss.map(
                      (acms) => _buildAgentCards(
                        acms,
                        cs,
                        tt,
                        ccc.lock && acms == ccc.agentCardModelss.last,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
        IconButton(
          onPressed: () async {
            await ccc.getAgentCardModels();
            setState(() {});
          },
          icon: Icon(Icons.send),
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

      return SizedBox(
        width: 720,
        child: Column(
          spacing: 24,
          children: [
            Row(
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
                            agentCardModel: acms[i],
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
                              agentCardModel: acms[i + 1],
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
        ),
      );
    } else {
      return SizedBox(
        width: 720,
        child: Column(
          spacing: 24,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${acms.where((e) => e.isSelected).length} Agents Selected',
                  style: tt.titleLarge?.copyWith(color: cs.onSurface),
                ),
                FilledButton(onPressed: null, child: Text('Confirm')),
              ],
            ),
            Column(
              spacing: 8,
              children: [
                for (int i = 0; i < acms.length; i += 2)
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    spacing: 8,
                    children: [
                      AgentCardWidget(agentCardModel: acms[i]),
                      if (i + 1 < acms.length) ...[
                        AgentCardWidget(agentCardModel: acms[i + 1]),
                      ],
                    ],
                  ),
              ],
            ),
          ],
        ),
      );
    }
  }

  Widget _buildAppBar(ChannelModel channelModel, TextTheme tt, ColorScheme cs) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 12, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            spacing: 12,
            children: [
              channelModel.getIcon(16),
              Text(
                channelModel.labelString,
                style: tt.titleLarge?.copyWith(color: cs.onSurface),
              ),
            ],
          ),
          Row(
            children: [
              TextButton.icon(
                icon: Icon(Icons.person),
                onPressed: () {},
                label: Text('${channelModel.agentsCount}'),
              ),
              IconButton(onPressed: () {}, icon: Icon(Icons.more_vert)),
            ],
          ),
        ],
      ),
    );
  }
}
