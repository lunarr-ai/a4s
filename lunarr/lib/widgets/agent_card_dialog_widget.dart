import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_card_model.dart';

class AgentCardDialogWidget extends StatelessWidget {
  final AgentCardModel agent;

  const AgentCardDialogWidget({super.key, required this.agent});

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
      backgroundColor: Theme.of(context).colorScheme.surfaceContainerHigh,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560, minWidth: 280),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(context),
              const SizedBox(height: 24),
              _buildSection(context, 'Description', agent.description),
              const SizedBox(height: 16),
              _buildSection(context, 'Instruction', agent.instruction),
              const SizedBox(height: 16),
              _buildSection(context, 'Model', agent.model),
              const SizedBox(height: 16),
              _buildListSection(context, 'Tools', agent.tools),
              const SizedBox(height: 16),
              _buildListSection(context, 'Knowledge', agent.knowledges),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Row(
      children: [
        CircleAvatar(
          radius: 20,
          backgroundImage: AssetImage(agent.iconString),
          onBackgroundImageError: (_, _) => const Icon(Icons.person),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                agent.name,
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              Text(
                agent.distributionList,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
        IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ],
    );
  }

  Widget _buildSection(BuildContext context, String title, String content) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(
            context,
          ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(content, style: Theme.of(context).textTheme.bodyMedium),
      ],
    );
  }

  Widget _buildListSection(
    BuildContext context,
    String title,
    List<String> items,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(
            context,
          ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        ...items.map(
          (item) => Padding(
            padding: const EdgeInsets.only(bottom: 2.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('• '),
                Expanded(
                  child: Text(
                    item,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
