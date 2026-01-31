import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_card_model.dart';

class AgentCardDialogWidget extends StatelessWidget {
  final AgentCardModel acm;

  const AgentCardDialogWidget({super.key, required this.acm});

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
      backgroundColor: Theme.of(context).colorScheme.surfaceContainerHigh,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560, minWidth: 280),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            spacing: 24,
            children: [
              _buildHeader(cs, tt, context),
              _buildSection(cs, tt, 'Description', acm.description),
              _buildSection(cs, tt, 'Instruction', acm.instruction),
              _buildSection(cs, tt, 'Model', acm.model),
              _buildListSection(cs, tt, 'Tools', acm.tools),
              _buildListSection(cs, tt, 'Knowledge', acm.knowledges),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(ColorScheme cs, TextTheme tt, BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          spacing: 12,
          children: [
            CircleAvatar(radius: 20, child: Image.asset(acm.iconString)),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  acm.name,
                  style: tt.titleMedium?.copyWith(
                    color: cs.onSurface,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  acm.distributionList,
                  style: tt.bodySmall?.copyWith(color: cs.onSurface),
                ),
              ],
            ),
          ],
        ),
        IconButton(
          icon: Icon(Icons.close, color: cs.onSurface),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ],
    );
  }

  Widget _buildSection(
    ColorScheme cs,
    TextTheme tt,
    String title,
    String body,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      spacing: 12,
      children: [
        Text(
          title,
          style: tt.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: cs.onSurface,
          ),
        ),
        Text(body, style: tt.bodyMedium?.copyWith(color: cs.onSurface)),
      ],
    );
  }

  Widget _buildListSection(
    ColorScheme cs,
    TextTheme tt,
    String title,
    List<String> bodies,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      spacing: 12,
      children: [
        Text(
          title,
          style: tt.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: cs.onSurface,
          ),
        ),
        ...bodies.map(
          (body) => Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('• ', style: tt.bodyMedium?.copyWith(color: cs.onSurface)),
              Text(body, style: tt.bodyMedium?.copyWith(color: cs.onSurface)),
            ],
          ),
        ),
      ],
    );
  }
}
