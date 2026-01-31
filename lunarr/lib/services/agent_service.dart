import 'package:lunarr/models/agent_model.dart';
import 'package:lunarr/services/user_service.dart';
import 'package:lunarr/services/workspace_service.dart';

class AgentService {
  AgentService._internal();

  static final AgentService _instance = AgentService._internal();

  factory AgentService() => _instance;

  List<AgentModel>? _agentModels;
  AgentModel? _agentModel;

  List<AgentModel>? get agentModels => _agentModels;
  AgentModel get agentModel => _agentModel ?? AgentModel('', '');

  // TODO: fetch agent models from user service and workspace service
  Future<void> fetchAgentModels() async {
    UserService userService = UserService();
    WorkspaceService workspaceService = WorkspaceService();

    _agentModels = [
      AgentModel('assets/avatars/1.png', 'Seungho\'s Agent'),
      AgentModel('assets/avatars/2.png', 'Kyungho\'s Agent'),
      AgentModel('assets/avatars/4.png', 'Minseok\'s Agent'),
    ];
    fetchAgentModel(0);
  }

  void fetchAgentModel(int index) {
    _agentModel = _agentModels![index];
  }
}
