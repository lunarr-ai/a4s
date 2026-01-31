import 'package:lunarr/models/channel_model.dart';

class ChannelService {
  ChannelService._internal();

  static final ChannelService _instance = ChannelService._internal();

  factory ChannelService() => _instance;

  List<ChannelModel>? _channelModels;
  ChannelModel? _channelModel;

  List<ChannelModel>? get channelModels => _channelModels;
  ChannelModel? get channelModel => _channelModel;

  Future<void> fetchChannelModels() async {
    _channelModels = [
      'All',
      'Frontend Team',
      'Backend Team',
      'Developers',
      'Lunch Group',
    ].map((labelString) => ChannelModel('', labelString, 10, 10)).toList();

    fetchChannelModel(0);
  }

  void fetchChannelModel(int index) {
    _channelModel = _channelModels![index];
  }
}
