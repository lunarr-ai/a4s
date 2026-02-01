import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/chat_model.dart';

enum ChannelChatType { question, selection, thinkings, answers }

class ChannelChatModel {
  final ChannelChatType type;
  final QuestionModel? questionModel;
  final SelectionModel? selectionModel;
  final List<ThinkingModel>? thinkingModels;
  final List<AnswerModel>? answerModels;

  ChannelChatModel.question(this.questionModel)
    : type = ChannelChatType.question,
      selectionModel = null,
      thinkingModels = null,
      answerModels = null;

  static ChannelChatModel questionExample() => ChannelChatModel.question((
    body:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
  ));

  ChannelChatModel.selection(this.selectionModel)
    : type = ChannelChatType.selection,
      questionModel = null,
      thinkingModels = null,
      answerModels = null;

  static ChannelChatModel selectionExample() => ChannelChatModel.selection((
    body: [
      AgentCardModel.seungho(false),
      AgentCardModel.kyungho(true),
      AgentCardModel.minseok(true),
      AgentCardModel.seungho(true),
    ],
  ));

  ChannelChatModel.thinkings(this.thinkingModels)
    : type = ChannelChatType.thinkings,
      questionModel = null,
      selectionModel = null,
      answerModels = null;

  static ChannelChatModel thinkingsExample(
    List<AgentCardModel> agentCardModels,
  ) => ChannelChatModel.thinkings(
    agentCardModels.map((e) => (agentCardModel: e, body: null)).toList(),
  );

  ChannelChatModel.answers(this.answerModels)
    : type = ChannelChatType.answers,
      selectionModel = null,
      questionModel = null,
      thinkingModels = null;

  static ChannelChatModel answersExample(
    List<AgentCardModel> agentCardModels,
  ) => ChannelChatModel.answers(
    agentCardModels
        .map(
          (e) => (
            agentCardModel: e,
            body: '''
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
''',
          ),
        )
        .toList(),
  );

  static List<ChannelChatModel> examples(
    List<AgentCardModel> agentCardModels,
  ) => [
    ChannelChatModel.questionExample(),
    ChannelChatModel.selectionExample(),
    ChannelChatModel.thinkingsExample(agentCardModels),
    ChannelChatModel.answersExample(agentCardModels),
  ];
}
