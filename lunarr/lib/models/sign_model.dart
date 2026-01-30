class SignModel {
  SignModel._internal();

  static final SignModel _instance = SignModel._internal();

  factory SignModel() => _instance;

  String? signInEmailAddress;
  String? signInPassword;
  String? firstName;
  String? lastName;
  String? birthday;
  String? gender;
  String? signUpEmailAddress;
  String? signUpPassword;
  String? confirm;
  String? code;

  void clear() {
    signInEmailAddress = signInPassword = firstName = lastName = birthday =
        gender = signUpEmailAddress = signUpPassword = confirm = code = null;
  }
}
