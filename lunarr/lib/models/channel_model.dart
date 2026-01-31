import 'package:flutter/material.dart';

class ChannelModel {
  ChannelModel(this.iconString, this.labelString, this.agentsCount);

  final String iconString;
  final String labelString;
  final int agentsCount;

  // Widget get icon => CircleAvatar(child: Image.network(iconString));
  Widget getIcon(double radius) => CircleAvatar(
    radius: radius,
    backgroundColor: Colors.transparent,
    child: Text('#'),
  );
}
