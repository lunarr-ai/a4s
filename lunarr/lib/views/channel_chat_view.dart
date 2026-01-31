import 'package:flutter/material.dart';
import 'package:lunarr/models/channel_model.dart';
import 'package:lunarr/services/channel_service.dart';
import 'package:lunarr/widgets/channel_chat_app_bar_widget.dart';

class ChannelChatView extends StatefulWidget {
  const ChannelChatView({super.key});

  @override
  State<ChannelChatView> createState() => _ChannelChatViewState();
}

class _ChannelChatViewState extends State<ChannelChatView> {
  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;
    final ChannelModel channelModel = ChannelService().channelModel!;

    return Column(children: [ChannelChatAppBarWidget()]);
  }
}
