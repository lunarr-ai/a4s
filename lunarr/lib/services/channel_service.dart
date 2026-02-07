import 'dart:convert';
import 'dart:developer';

import 'package:http/http.dart' as http;
import 'package:lunarr/models/channel_model.dart';

const _baseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8000',
);

class ChannelService {
  ChannelService._internal();

  static final ChannelService _instance = ChannelService._internal();

  factory ChannelService() => _instance;

  List<ChannelModel>? _channelModels;
  ChannelModel? _channelModel;

  List<ChannelModel>? get channelModels => _channelModels;
  ChannelModel get channelModel =>
      _channelModel ??
      ChannelModel(id: '', name: '', description: '', ownerId: '');

  Future<void> fetchChannelModels() async {
    try {
      final uri = Uri.parse('$_baseUrl/api/v1/channels');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final listResponse = ChannelListResponse.fromJson(data);
        _channelModels = listResponse.channels;

        if (_channelModels!.isNotEmpty) {
          fetchChannelModel(0);
        }
        return;
      }
      log('Failed to fetch channels: ${response.statusCode}');
    } catch (e) {
      log('Error fetching channels: $e');
    }

    _useMockData();
  }

  void _useMockData() {
    _channelModels = [
      ChannelModel.all(),
      ChannelModel.frontendTeam(),
      ChannelModel.backendTeam(),
      ChannelModel.developers(),
      ChannelModel.lunchGroup(),
    ];
    fetchChannelModel(0);
  }

  void fetchChannelModel(int index) {
    if (_channelModels != null && index < _channelModels!.length) {
      _channelModel = _channelModels![index];
    }
  }

  Future<ChannelChatResponse?> sendChannelMessage(
    String channelId,
    String message, {
    List<String>? agentIds,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/v1/channels/$channelId/chat');
      final payload = <String, dynamic>{'message': message};
      if (agentIds != null) {
        payload['agent_ids'] = agentIds;
      }

      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ChannelChatResponse.fromJson(data);
      }
      log('Failed to send channel message: ${response.statusCode}');
    } catch (e) {
      log('Error sending channel message: $e');
    }
    return null;
  }
}
