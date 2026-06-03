import Foundation
import StoreKit

/// Single source of truth for IAP state. Owned by `JBGlossaryApp` as a
/// `@StateObject` and injected via `.environmentObject` so every view can
/// read `isUnlocked(_:)` and call `purchase(_:)` / `restorePurchases()`.
@MainActor
final class PurchaseManager: ObservableObject {
    /// Industries the user has directly purchased (excludes the always-free
    /// anchor and the master unlock — those are handled by `isUnlocked`).
    @Published private(set) var purchasedIndustries: Set<IndustryID> = []

    /// True if the user owns the master "All Industries" IAP or was
    /// grandfathered in on first v2 launch.
    @Published private(set) var hasMasterUnlock: Bool = false

    /// StoreKit products keyed by identifier. Loaded on init; empty if the
    /// device has no network or App Store Connect setup is incomplete.
    @Published private(set) var products: [Product] = []

    @Published private(set) var lastError: String?

    private var updateListenerTask: Task<Void, Never>?

    init() {
        startListeningForTransactions()
        Task { await refresh() }
    }

    deinit {
        updateListenerTask?.cancel()
    }

    /// True if the user owns the full industry (every letter, A–Z) — either
    /// via the industry's IAP or the master "All Industries" unlock. Letters
    /// A–D are free regardless of this return value; use `isLocked(letter:in:)`
    /// for letter-level checks.
    func isUnlocked(_ id: IndustryID) -> Bool {
        hasMasterUnlock || purchasedIndustries.contains(id)
    }

    /// True if the given letter is gated behind the industry's paywall for
    /// the current user (outside A–D and the user doesn't own the industry).
    func isLocked(letter: String, in id: IndustryID) -> Bool {
        if IndustryConfig.freeLetters.contains(letter) { return false }
        return !isUnlocked(id)
    }

    /// True if a term is locked. Convenience over `isLocked(letter:in:)`.
    func isLocked(_ term: Term, in id: IndustryID) -> Bool {
        isLocked(letter: term.letter, in: id)
    }

    /// StoreKit `Product` for an industry's IAP, if loaded.
    func product(for id: IndustryID) -> Product? {
        let productID = IndustryConfig.config(for: id).iapProductID
        return products.first { $0.id == productID }
    }

    /// The master "All Industries" `Product`, if loaded.
    var masterProduct: Product? {
        products.first { $0.id == masterUnlockProductID }
    }

    /// Initiate a purchase. Returns true on success, false on user-cancel,
    /// pending, or error. UI should dismiss any paywall sheet on true.
    @discardableResult
    func purchase(_ product: Product) async -> Bool {
        do {
            let result = try await product.purchase()
            switch result {
            case .success(let verification):
                let transaction = try checkVerified(verification)
                await transaction.finish()
                await updateEntitlements()
                return true
            case .userCancelled, .pending:
                return false
            @unknown default:
                return false
            }
        } catch {
            lastError = error.localizedDescription
            return false
        }
    }

    func restorePurchases() async {
        do {
            try await AppStore.sync()
        } catch {
            lastError = error.localizedDescription
        }
        await refresh()
    }

    // MARK: - Internals

    /// Local flag set by `checkGrandfathering()`. Persists across launches so
    /// the AppTransaction call only has to succeed once.
    private static let grandfatheredKey = "jbglossary.grandfathered.masterUnlock"

    private func refresh() async {
        await loadProducts()
        await updateEntitlements()
        await checkGrandfathering()
    }

    private func loadProducts() async {
        let productIDs = IndustryConfig.all.map(\.iapProductID) + [masterUnlockProductID]
        do {
            products = try await Product.products(for: productIDs)
        } catch {
            lastError = error.localizedDescription
        }
    }

    private func updateEntitlements() async {
        var owned: Set<IndustryID> = []
        var master = UserDefaults.standard.bool(forKey: Self.grandfatheredKey)

        for await result in Transaction.currentEntitlements {
            guard case .verified(let transaction) = result else { continue }
            if transaction.productID == masterUnlockProductID {
                master = true
                continue
            }
            for config in IndustryConfig.all where config.iapProductID == transaction.productID {
                owned.insert(config.id)
                break
            }
        }

        purchasedIndustries = owned
        hasMasterUnlock = master
    }

    /// First v2 launch: if `AppTransaction.originalAppVersion` starts with
    /// "1." the user installed a pre-v2 JB Pharma build, so we grant the
    /// master "All Industries" unlock as a thank-you. Persists locally so
    /// the check only runs until it succeeds.
    ///
    /// `AppTransaction.shared` can fail in the simulator before a receipt
    /// is available — that's fine, the check retries on every launch until
    /// the flag is set.
    private func checkGrandfathering() async {
        guard !UserDefaults.standard.bool(forKey: Self.grandfatheredKey) else { return }
        do {
            let result = try await AppTransaction.shared
            guard case .verified(let appTransaction) = result else { return }
            // Only grandfather genuine production installs. In the sandbox and
            // Xcode StoreKit environments `originalAppVersion` is always "1.0",
            // which would grant the master unlock to the App Review team and
            // hide every paywall behind an all-unlocked state.
            // (App Review rejection, Guideline 2.1(b), 2026-06-03.)
            guard appTransaction.environment == .production else { return }
            if appTransaction.originalAppVersion.hasPrefix("1.") {
                UserDefaults.standard.set(true, forKey: Self.grandfatheredKey)
                await updateEntitlements()
            }
        } catch {
            // Retry next launch.
        }
    }

    private func startListeningForTransactions() {
        updateListenerTask = Task { [weak self] in
            for await result in Transaction.updates {
                guard let self else { return }
                guard case .verified(let transaction) = result else { continue }
                await transaction.finish()
                await self.updateEntitlements()
            }
        }
    }

    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified(_, let error): throw error
        case .verified(let safe): return safe
        }
    }
}
