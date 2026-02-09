import 'package:flutter/material.dart';
import 'package:lunarr/constants/colors.dart';
import 'package:lunarr/services/agent_card_service.dart';
import 'package:lunarr/services/channel_service.dart';
import 'package:lunarr/services/user_service.dart';
import 'package:lunarr/views/main_view.dart';
import 'package:lunarr/widgets/emblem_widget.dart';

class SignDemoView extends StatefulWidget {
  const SignDemoView({super.key});

  @override
  State<SignDemoView> createState() => _SignDemoViewState();
}

class _SignDemoViewState extends State<SignDemoView> {
  final usernameController = TextEditingController();

  @override
  void dispose() {
    usernameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: LUNARR_COLOR),
        child: Center(
          child: Container(
            padding: const EdgeInsets.all(24),
            constraints: BoxConstraints(maxWidth: 480),
            decoration: BoxDecoration(
              color: cs.surface.withAlpha(128),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              spacing: 24,
              children: [
                EmblemWidget(tt: tt, cs: cs),
                Column(
                  spacing: 24,
                  children: [
                    TextField(
                      controller: usernameController,
                      onChanged: (value) => UserService().username = value,
                      decoration: InputDecoration(labelText: 'Username'),
                      onSubmitted: (_) async {
                        await ChannelService().fetchChannelModels();
                        await AgentCardService().fetchAgentCardModels();

                        Navigator.of(context).pushReplacement(
                          MaterialPageRoute(builder: (context) => MainView()),
                        );
                      },
                    ),
                    Row(
                      mainAxisSize: MainAxisSize.max,
                      children: [
                        Expanded(
                          child: FilledButton(
                            onPressed: () async {
                              await ChannelService().fetchChannelModels();
                              await AgentCardService().fetchAgentCardModels();

                              Navigator.of(context).pushReplacement(
                                MaterialPageRoute(
                                  builder: (context) => MainView(),
                                ),
                              );
                            },
                            child: Text('Try Demo'),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
