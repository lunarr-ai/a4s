class UserModel {
  UserModel._internal();

  static final UserModel _instance = UserModel._internal();

  factory UserModel() => _instance;
}
