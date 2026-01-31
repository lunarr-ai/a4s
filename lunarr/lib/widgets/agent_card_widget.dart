import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/widgets/agent_card_dialog_widget.dart';

class AgentCardWidget extends StatefulWidget {
  final AgentCardModel agentCardModel;
  final VoidCallback? onTap;

  const AgentCardWidget({super.key, required this.agentCardModel, this.onTap});

  @override
  State<AgentCardWidget> createState() => _AgentCardWidgetState();
}

class _AgentCardWidgetState extends State<AgentCardWidget> {
  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;

    return SizedBox(
      width: 356,
      child: Card.outlined(
        color: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: widget.agentCardModel.isSelected
                ? cs.primary
                : cs.outlineVariant,
          ),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: widget.onTap != null
              ? () {
                  setState(() {
                    widget.agentCardModel.isSelected =
                        !widget.agentCardModel.isSelected;
                    widget.onTap?.call();
                  });
                }
              : null,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 4, 12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      spacing: 12,
                      children: [
                        CircleAvatar(
                          radius: 20,
                          child: Image.asset(widget.agentCardModel.iconString),
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              widget.agentCardModel.name,
                              style: tt.titleMedium?.copyWith(
                                color: cs.onSurface,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              widget.agentCardModel.distributionList,
                              style: tt.bodyMedium?.copyWith(
                                color: cs.onSurface,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    MenuAnchor(
                      builder:
                          (
                            BuildContext context,
                            MenuController controller,
                            Widget? child,
                          ) {
                            return IconButton(
                              onPressed: () {
                                if (controller.isOpen) {
                                  controller.close();
                                } else {
                                  controller.open();
                                }
                              },
                              icon: const Icon(Icons.more_vert),
                              tooltip: 'Show menu',
                            );
                          },
                      menuChildren: [
                        MenuItemButton(
                          onPressed: () => showDialog(
                            context: context,
                            builder: (context) => AgentCardDialogWidget(
                              agent: widget.agentCardModel,
                            ),
                          ),
                          child: const Text('Details'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  widget.agentCardModel.description,
                  style: tt.bodyMedium?.copyWith(color: cs.onSurface),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
