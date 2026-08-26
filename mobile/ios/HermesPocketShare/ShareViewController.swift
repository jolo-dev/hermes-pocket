import UIKit

final class ShareViewController: UIViewController {
  override func viewDidLoad() {
    super.viewDidLoad()
    view.backgroundColor = .systemBackground

    let titleLabel = UILabel()
    titleLabel.font = .preferredFont(forTextStyle: .title2)
    titleLabel.numberOfLines = 0
    titleLabel.text = "Review in Hermes Pocket"

    let detailLabel = UILabel()
    detailLabel.font = .preferredFont(forTextStyle: .body)
    detailLabel.numberOfLines = 0
    detailLabel.text = "Share intake is not enabled in this development build. Nothing has been copied or sent."

    let cancelButton = UIButton(type: .system)
    cancelButton.setTitle("Cancel", for: .normal)
    cancelButton.addTarget(self, action: #selector(cancelShare), for: .touchUpInside)

    let stack = UIStackView(arrangedSubviews: [titleLabel, detailLabel, cancelButton])
    stack.axis = .vertical
    stack.spacing = 20
    stack.translatesAutoresizingMaskIntoConstraints = false
    view.addSubview(stack)

    NSLayoutConstraint.activate([
      stack.leadingAnchor.constraint(equalTo: view.layoutMarginsGuide.leadingAnchor),
      stack.trailingAnchor.constraint(equalTo: view.layoutMarginsGuide.trailingAnchor),
      stack.centerYAnchor.constraint(equalTo: view.centerYAnchor),
    ])
  }

  @objc private func cancelShare() {
    extensionContext?.cancelRequest(withError: NSError(
      domain: "com.hermespocket.share",
      code: 1,
      userInfo: [NSLocalizedDescriptionKey: "Share cancelled without staging content"]
    ))
  }
}
