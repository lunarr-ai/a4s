import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_model.dart';
import 'package:lunarr/services/agent_service.dart';

class AgentChatAppBarWidget extends StatelessWidget {
  const AgentChatAppBarWidget({super.key});

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;
    final AgentModel agentModel = AgentService().agentModel!;

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
              IconButton(onPressed: () {}, icon: Icon(Icons.more_vert)),
            ],
          ),
        ],
      ),
    );
  }
}
