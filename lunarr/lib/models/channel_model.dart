import 'package:flutter/material.dart';

class ChannelModel {
  final String id;
  final String name;
  final String description;
  final List<String> agentIds;
  final String ownerId;

  ChannelModel({
    required this.id,
    required this.name,
    required this.description,
    this.agentIds = const [],
    required this.ownerId,
  });

  factory ChannelModel.fromJson(Map<String, dynamic> json) {
    return ChannelModel(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String? ?? '',
      agentIds: (json['agent_ids'] as List<dynamic>?)?.cast<String>() ?? [],
      ownerId: json['owner_id'] as String,
    );
  }

  int get agentsCount => agentIds.length;
  String get labelString => name;
  String get iconString => '';

  Widget getIcon(double radius) => CircleAvatar(
    radius: radius,
    backgroundColor: Colors.transparent,
    child: const Text('#'),
  );

  static ChannelModel all() => ChannelModel(
    id: 'all',
    name: 'All',
    description: 'All agents',
    ownerId: 'system',
  );

  static ChannelModel frontendTeam() => ChannelModel(
    id: 'frontend-team',
    name: 'Frontend Team',
    description: 'Frontend development agents',
    ownerId: 'system',
  );

  static ChannelModel backendTeam() => ChannelModel(
    id: 'backend-team',
    name: 'Backend Team',
    description: 'Backend development agents',
    ownerId: 'system',
  );

  static ChannelModel developers() => ChannelModel(
    id: 'developers',
    name: 'Developers',
    description: 'All developer agents',
    ownerId: 'system',
  );

  static ChannelModel lunchGroup() => ChannelModel(
    id: 'lunch-group',
    name: 'Lunch Group',
    description: 'Lunch coordination agents',
    ownerId: 'system',
  );
}

class ChannelListResponse {
  final List<ChannelModel> channels;
  final int total;

  ChannelListResponse({required this.channels, required this.total});

  factory ChannelListResponse.fromJson(Map<String, dynamic> json) {
    return ChannelListResponse(
      channels: (json['channels'] as List<dynamic>)
          .map((e) => ChannelModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: json['total'] as int? ?? 0,
    );
  }
}

class AgentChatResult {
  final String agentId;
  final String agentName;
  final String? response;
  final String? error;

  AgentChatResult({
    required this.agentId,
    required this.agentName,
    this.response,
    this.error,
  });

  factory AgentChatResult.fromJson(Map<String, dynamic> json) {
    return AgentChatResult(
      agentId: json['agent_id'] as String,
      agentName: json['agent_name'] as String,
      response: json['response'] as String?,
      error: json['error'] as String?,
    );
  }
}

enum ChannelChatResponseType { candidates, direct, results }

class CandidateAgent {
  final String id;
  final String name;
  final String reason;

  CandidateAgent({required this.id, required this.name, this.reason = ''});

  factory CandidateAgent.fromJson(Map<String, dynamic> json) {
    return CandidateAgent(
      id: json['id'] as String,
      name: json['name'] as String,
      reason: json['reason'] as String? ?? '',
    );
  }
}

class ChannelChatResponse {
  final ChannelChatResponseType type;
  final List<CandidateAgent>? candidates;
  final String? directResponse;
  final List<AgentChatResult>? results;

  ChannelChatResponse({
    required this.type,
    this.candidates,
    this.directResponse,
    this.results,
  });

  factory ChannelChatResponse.fromJson(Map<String, dynamic> json) {
    final typeStr = json['type'] as String;
    final type = ChannelChatResponseType.values.firstWhere(
      (e) => e.name == typeStr,
      orElse: () => ChannelChatResponseType.results,
    );

    return ChannelChatResponse(
      type: type,
      candidates: json['candidates'] != null
          ? (json['candidates'] as List<dynamic>)
                .map((e) => CandidateAgent.fromJson(e as Map<String, dynamic>))
                .toList()
          : null,
      directResponse: json['direct_response'] as String?,
      results: json['results'] != null
          ? (json['results'] as List<dynamic>)
                .map((e) => AgentChatResult.fromJson(e as Map<String, dynamic>))
                .toList()
          : null,
    );
  }
}
