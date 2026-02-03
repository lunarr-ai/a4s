import 'package:lunarr/models/agent.dart';

class AgentCardModel {
  final String id;
  final String iconString;
  final String name;
  final String distributionList;
  final String description;
  final String instruction;
  final String model;
  final List<String> tools;
  final List<String> knowledges;
  bool isSelected;

  AgentCardModel({
    this.id = '',
    required this.iconString,
    required this.name,
    required this.distributionList,
    required this.description,
    required this.instruction,
    required this.model,
    required this.tools,
    required this.knowledges,
    required this.isSelected,
  });

  factory AgentCardModel.fromAgent(
    Agent agent, {
    bool isSelected = false,
    int avatarIndex = 1,
  }) {
    return AgentCardModel(
      id: agent.id,
      iconString: 'assets/avatars/$avatarIndex.png',
      name: agent.name,
      distributionList: agent.ownerId,
      description: agent.description,
      instruction: agent.spawnConfig?.instruction ?? '',
      model: agent.spawnConfig?.model.displayName ?? 'Unknown',
      tools: agent.spawnConfig?.tools ?? [],
      knowledges: [],
      isSelected: isSelected,
    );
  }

  static AgentCardModel seungho(bool isSelected) {
    return AgentCardModel(
      iconString: 'assets/avatars/1.png',
      name: 'Seungho\'s Agent',
      distributionList: 'Frontend Team',
      description:
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
      instruction:
          'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
      model: 'Gemini 3.0 Pro',
      tools: [
        'Lorem ipsum',
        'dolor sit amet',
        'consectetur',
        'adipiscing elit',
      ],
      knowledges: [
        'Lorem ipsum dolor sit amet',
        'consectetur adipiscing elit',
        'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua',
      ],
      isSelected: isSelected,
    );
  }

  static AgentCardModel kyungho(bool isSelected) {
    return AgentCardModel(
      iconString: 'assets/avatars/2.png',
      name: 'Kyungho\'s Agent',
      distributionList: 'Backend Team',
      description:
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
      instruction:
          'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
      model: 'Gemini 3.0 Pro',
      tools: [
        'Lorem ipsum',
        'dolor sit amet',
        'consectetur',
        'adipiscing elit',
      ],
      knowledges: [
        'Lorem ipsum dolor sit amet',
        'consectetur adipiscing elit',
        'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua',
      ],
      isSelected: isSelected,
    );
  }

  static AgentCardModel minseok(bool isSelected) {
    return AgentCardModel(
      iconString: 'assets/avatars/4.png',
      name: 'Minseok\'s Agent',
      distributionList: 'Backend Team',
      description:
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
      instruction:
          'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
      model: 'Gemini 3.0 Pro',
      tools: [
        'Lorem ipsum',
        'dolor sit amet',
        'consectetur',
        'adipiscing elit',
      ],
      knowledges: [
        'Lorem ipsum dolor sit amet',
        'consectetur adipiscing elit',
        'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua',
      ],
      isSelected: isSelected,
    );
  }
}
