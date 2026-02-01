import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/chat_model.dart';

enum AgentChatType { question, selection, thinking, answer }

class AgentChatModel {
  final AgentChatType type;
  final QuestionModel? questionModel;
  final SelectionModel? selectionModel;
  final ThinkingModel? thinkingModel;
  final AnswerModel? answerModel;

  AgentChatModel.question(this.questionModel)
    : type = AgentChatType.question,
      selectionModel = null,
      thinkingModel = null,
      answerModel = null;

  static AgentChatModel questionExample() => AgentChatModel.question((
    body:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
  ));

  AgentChatModel.selection(this.selectionModel)
    : type = AgentChatType.selection,
      questionModel = null,
      thinkingModel = null,
      answerModel = null;

  static AgentChatModel selectionExample() => AgentChatModel.selection((
    body: [
      AgentCardModel.seungho(false),
      AgentCardModel.kyungho(true),
      AgentCardModel.minseok(true),
      AgentCardModel.seungho(true),
    ],
  ));

  AgentChatModel.thinking(this.thinkingModel)
    : type = AgentChatType.thinking,
      questionModel = null,
      selectionModel = null,
      answerModel = null;

  static AgentChatModel thinkingExample(AgentCardModel agentCardModel) =>
      AgentChatModel.thinking((agentCardModel: agentCardModel, body: null));

  AgentChatModel.answer(this.answerModel)
    : type = AgentChatType.answer,
      selectionModel = null,
      questionModel = null,
      thinkingModel = null;

  static AgentChatModel answerExample(AgentCardModel agentCardModel) =>
      AgentChatModel.answer((
        agentCardModel: agentCardModel,
        body: '''
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
''',
      ));

  static List<AgentChatModel> examples(AgentCardModel agentCardModel) => [
    AgentChatModel.questionExample(),
    AgentChatModel.selectionExample(),
    AgentChatModel.thinkingExample(agentCardModel),
    AgentChatModel.answerExample(agentCardModel),
  ];
}
