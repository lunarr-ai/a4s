import 'package:flutter/material.dart';
import 'package:lunarr/models/agent.dart';

class AgentModel {
  final String id;
  final String iconString;
  final String labelString;
  final Agent? agent;

  AgentModel(this.iconString, this.labelString, {this.id = '', this.agent});

  Widget getIcon(double radius) =>
      CircleAvatar(radius: radius, child: Image.asset(iconString));

  factory AgentModel.fromAgent(Agent agent, {int avatarIndex = 1}) {
    return AgentModel(
      'assets/avatars/$avatarIndex.png',
      agent.name,
      id: agent.id,
      agent: agent,
    );
  }

  static AgentModel seungho() =>
      AgentModel('assets/avatars/1.png', 'Seungho\'s Agent');
  static AgentModel kyungho() =>
      AgentModel('assets/avatars/2.png', 'Kyungho\'s Agent');
  static AgentModel minseok() =>
      AgentModel('assets/avatars/4.png', 'Minseok\'s Agent');
}
