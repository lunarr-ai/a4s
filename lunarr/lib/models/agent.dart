enum AgentStatus { pending, running, stopped, error }

enum AgentMode { serverless, permanent }

enum ModelProvider { openai, anthropic, google, openrouter }

class AgentModelConfig {
  final ModelProvider provider;
  final String modelId;

  AgentModelConfig({required this.provider, required this.modelId});

  factory AgentModelConfig.fromJson(Map<String, dynamic> json) {
    return AgentModelConfig(
      provider: ModelProvider.values.firstWhere(
        (e) => e.name == json['provider'],
        orElse: () => ModelProvider.google,
      ),
      modelId: json['model_id'] as String? ?? '',
    );
  }

  String get displayName {
    final providerName =
        provider.name[0].toUpperCase() + provider.name.substring(1);
    return '$providerName $modelId';
  }
}

class SpawnConfig {
  final String image;
  final AgentModelConfig model;
  final String instruction;
  final List<String> tools;

  SpawnConfig({
    required this.image,
    required this.model,
    required this.instruction,
    required this.tools,
  });

  factory SpawnConfig.fromJson(Map<String, dynamic> json) {
    return SpawnConfig(
      image: json['image'] as String? ?? '',
      model: AgentModelConfig.fromJson(json['model'] as Map<String, dynamic>),
      instruction: json['instruction'] as String? ?? '',
      tools: (json['tools'] as List<dynamic>?)?.cast<String>() ?? [],
    );
  }
}

class Agent {
  final String id;
  final String name;
  final String description;
  final String version;
  final String url;
  final int port;
  final String ownerId;
  final AgentStatus status;
  final DateTime createdAt;
  final AgentMode mode;
  final SpawnConfig? spawnConfig;

  Agent({
    required this.id,
    required this.name,
    required this.description,
    required this.version,
    required this.url,
    required this.port,
    required this.ownerId,
    required this.status,
    required this.createdAt,
    required this.mode,
    this.spawnConfig,
  });

  factory Agent.fromJson(Map<String, dynamic> json) {
    return Agent(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String? ?? '',
      version: json['version'] as String? ?? '1.0.0',
      url: json['url'] as String? ?? '',
      port: json['port'] as int? ?? 8000,
      ownerId: json['owner_id'] as String? ?? '',
      status: AgentStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => AgentStatus.pending,
      ),
      createdAt: DateTime.parse(
          json['created_at'] as String? ?? DateTime.now().toIso8601String()),
      mode: AgentMode.values.firstWhere(
        (e) => e.name == json['mode'],
        orElse: () => AgentMode.serverless,
      ),
      spawnConfig: json['spawn_config'] != null
          ? SpawnConfig.fromJson(json['spawn_config'] as Map<String, dynamic>)
          : null,
    );
  }
}

class AgentListResponse {
  final List<Agent> agents;
  final int offset;
  final int limit;
  final int total;

  AgentListResponse({
    required this.agents,
    required this.offset,
    required this.limit,
    required this.total,
  });

  factory AgentListResponse.fromJson(Map<String, dynamic> json) {
    return AgentListResponse(
      agents: (json['agents'] as List<dynamic>)
          .map((e) => Agent.fromJson(e as Map<String, dynamic>))
          .toList(),
      offset: json['offset'] as int? ?? 0,
      limit: json['limit'] as int? ?? 50,
      total: json['total'] as int? ?? 0,
    );
  }
}
