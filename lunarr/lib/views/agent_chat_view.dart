import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_model.dart';
import 'package:lunarr/services/agent_service.dart';
import 'package:lunarr/widgets/agent_chat_app_bar_widget.dart';

class AgentChatView extends StatefulWidget {
  const AgentChatView({super.key});

  @override
  State<AgentChatView> createState() => _AgentChatViewState();
}

class _AgentChatViewState extends State<AgentChatView> {
  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;
    AgentModel agentModel = AgentService().agentModel!;

    return Column(children: [AgentChatAppBarWidget()]);
  }
}
