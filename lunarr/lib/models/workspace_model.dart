class WorkspaceModel {
  WorkspaceModel._internal();

  static final WorkspaceModel _instance = WorkspaceModel._internal();

  factory WorkspaceModel() => _instance;
}
