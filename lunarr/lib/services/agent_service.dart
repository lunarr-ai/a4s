import 'dart:convert';
import 'dart:developer';

import 'package:http/http.dart' as http;
import 'package:lunarr/models/agent.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/agent_model.dart';

const _baseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8080',
);

class AgentService {
  AgentService._internal();

  static final AgentService _instance = AgentService._internal();

  factory AgentService() => _instance;

  List<Agent> _agents = [];
  List<AgentModel>? _agentModels;
  AgentModel? _agentModel;

  List<Agent> get agents => _agents;
  List<AgentModel>? get agentModels => _agentModels;
  AgentModel get agentModel => _agentModel ?? AgentModel('', '');

  Future<void> fetchAgentModels() async {
    try {
      final uri = Uri.parse('$_baseUrl/api/v1/agents');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final listResponse = AgentListResponse.fromJson(data);
        _agents = listResponse.agents;
        _agentModels = _agents
            .asMap()
            .entries
            .map(
              (e) =>
                  AgentModel.fromAgent(e.value, avatarIndex: (e.key % 30) + 1),
            )
            .toList();

        if (_agentModels!.isNotEmpty) {
          fetchAgentModel(0);
        }
        return;
      }
      log('Failed to fetch agents: ${response.statusCode}');
    } catch (e) {
      log('Error fetching agents: $e');
    }

    _useMockData();
  }

  void _useMockData() {
    _agents = [];
    _agentModels = [
      AgentModel.seungho(),
      AgentModel.kyungho(),
      AgentModel.minseok(),
    ];
    fetchAgentModel(0);
  }

  void fetchAgentModel(int index) {
    if (_agentModels != null && index < _agentModels!.length) {
      _agentModel = _agentModels![index];
    }
  }

  Future<List<Agent>> searchAgents(String query, {int limit = 5}) async {
    try {
      final uri = Uri.parse(
        '$_baseUrl/api/v1/agents/search?query=${Uri.encodeComponent(query)}&limit=$limit',
      );
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final searchResponse = AgentSearchResponse.fromJson(data);
        return searchResponse.agents;
      }
      log('Failed to search agents: ${response.statusCode}');
    } catch (e) {
      log('Error searching agents: $e');
    }
    return [];
  }

  Agent? getAgentById(String id) {
    try {
      return _agents.firstWhere((a) => a.id == id);
    } catch (_) {
      return null;
    }
  }

  AgentCardModel getAgentCardModel(int index, {bool isSelected = false}) {
    if (index < _agents.length) {
      return AgentCardModel.fromAgent(
        _agents[index],
        isSelected: isSelected,
        avatarIndex: (index % 30) + 1,
      );
    }

    return switch (index) {
      0 => AgentCardModel.seungho(isSelected),
      1 => AgentCardModel.kyungho(isSelected),
      _ => AgentCardModel.minseok(isSelected),
    };
  }

  Future<String?> sendMessage(String agentId, String message) async {
    try {
      final uri = Uri.parse('$_baseUrl/agents/$agentId/');
      final requestId = DateTime.now().microsecondsSinceEpoch.toString();
      final messageId = (DateTime.now().microsecondsSinceEpoch + 1).toString();

      final body = jsonEncode({
        'jsonrpc': '2.0',
        'id': requestId,
        'method': 'message/send',
        'params': {
          'message': {
            'role': 'user',
            'parts': [
              {'kind': 'text', 'text': message},
            ],
            'messageId': messageId,
          },
        },
      });

      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: body,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return _extractTextFromA2AResponse(data);
      }
      log('Failed to send message: ${response.statusCode}');
    } catch (e) {
      log('Error sending message: $e');
    }
    return null;
  }

  String? _extractTextFromA2AResponse(Map<String, dynamic> data) {
    final result = data['result'] as Map<String, dynamic>?;
    if (result == null) return null;

    final textParts = <String>[];

    final artifacts = result['artifacts'] as List<dynamic>?;
    if (artifacts != null) {
      for (final artifact in artifacts) {
        final parts =
            (artifact as Map<String, dynamic>)['parts'] as List<dynamic>?;
        if (parts != null) {
          for (final part in parts) {
            final text = (part as Map<String, dynamic>)['text'] as String?;
            if (text != null) textParts.add(text);
          }
        }
      }
    }

    final parts = result['parts'] as List<dynamic>?;
    if (parts != null) {
      for (final part in parts) {
        final text = (part as Map<String, dynamic>)['text'] as String?;
        if (text != null) textParts.add(text);
      }
    }

    final status = result['status'] as Map<String, dynamic>?;
    if (status != null) {
      final statusMessage = status['message'] as Map<String, dynamic>?;
      if (statusMessage != null) {
        final statusParts = statusMessage['parts'] as List<dynamic>?;
        if (statusParts != null) {
          for (final part in statusParts) {
            final text = (part as Map<String, dynamic>)['text'] as String?;
            if (text != null) textParts.add(text);
          }
        }
      }
    }

    return textParts.isNotEmpty ? textParts.join('\n') : null;
  }
}
