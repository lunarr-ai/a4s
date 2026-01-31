import 'package:lunarr/models/channel_model.dart';
import 'package:lunarr/services/user_service.dart';
import 'package:lunarr/services/workspace_service.dart';

class ChannelService {
  ChannelService._internal();

  static final ChannelService _instance = ChannelService._internal();

  factory ChannelService() => _instance;

  List<ChannelModel>? _channelModels;
  ChannelModel? _channelModel;

  List<ChannelModel>? get channelModels => _channelModels;
  ChannelModel? get channelModel => _channelModel;

  // TODO: fetch channel models from user service and workspace service
  Future<void> fetchChannelModels() async {
    UserService userService = UserService();
    WorkspaceService workspaceService = WorkspaceService();

    _channelModels = [
      'All',
      'Frontend Team',
      'Backend Team',
      'Developers',
      'Lunch Group',
    ].map((labelString) => ChannelModel('', labelString, 10)).toList();

    fetchChannelModel(0);
  }

  void fetchChannelModel(int index) {
    _channelModel = _channelModels![index];
  }
}
