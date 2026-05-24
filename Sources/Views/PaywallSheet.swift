import SwiftUI
import StoreKit

/// Shown when the user taps a locked industry tile in `IndustryPickerView`.
/// Previews a handful of the industry's terms, offers the per-industry
/// purchase + "All Industries" master upgrade, and surfaces the required
/// "Restore Purchases" and terms/privacy links.
struct PaywallSheet: View {
    let targetIndustry: IndustryID
    @EnvironmentObject var purchases: PurchaseManager
    @Environment(\.dismiss) private var dismiss

    @State private var isPurchasing = false
    @State private var sampleTerms: [Term] = []
    @State private var lockedCount: Int = 0

    private var config: IndustryConfig {
        IndustryConfig.config(for: targetIndustry)
    }

    var body: some View {
        ZStack {
            PGColors.bg.ignoresSafeArea()
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    header
                    if !sampleTerms.isEmpty {
                        previewSection
                    }
                    ctaSection
                    restoreSection
                    legalSection
                }
                .padding(.horizontal, 20)
                .padding(.top, 24)
                .padding(.bottom, 32)
            }
        }
        .task { await loadSampleTerms() }
    }

    // MARK: - Header

    private var header: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline, spacing: 6) {
                Text("JB")
                    .font(PGFont.jbStamp)
                    .foregroundStyle(PGColors.ink)
                Text(config.brand.titleBody)
                    .font(PGFont.displayItalic)
                    .foregroundStyle(config.brand.primaryColor)
            }
            Text(config.brand.subtitle)
                .font(PGFont.metaItalic)
                .foregroundStyle(PGColors.inkLight)
            if lockedCount > 0 {
                Text("You have letters A–D free. Unlock E–Z to read \(lockedCount) more terms.")
                    .font(PGFont.metaItalic)
                    .foregroundStyle(PGColors.inkLight)
                    .padding(.top, 4)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    // MARK: - Preview

    private var previewSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("A FEW LOCKED ENTRIES")
                .font(PGFont.eyebrow)
                .tracking(0.8)
                .foregroundStyle(PGColors.inkLight)

            VStack(spacing: 0) {
                ForEach(sampleTerms) { term in
                    HStack(alignment: .firstTextBaseline) {
                        Text(term.term)
                            .font(PGFont.termRowTitle)
                            .foregroundStyle(PGColors.ink)
                        if term.hasFull {
                            Text(term.full)
                                .font(PGFont.termRowFullItalic)
                                .foregroundStyle(PGColors.inkLight)
                                .lineLimit(1)
                        }
                        Spacer()
                    }
                    .padding(.vertical, 10)
                    .padding(.horizontal, 14)
                    if term.id != sampleTerms.last?.id {
                        Divider().background(PGColors.inkRule)
                    }
                }
            }
            .background(PGColors.card)
            .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(PGColors.cardBorder, lineWidth: 1)
            )
            .overlay(alignment: .bottom) {
                LinearGradient(
                    colors: [PGColors.bg.opacity(0), PGColors.bg],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .frame(height: 60)
                .allowsHitTesting(false)
            }
        }
    }

    // MARK: - CTAs

    private var ctaSection: some View {
        VStack(spacing: 10) {
            if let product = purchases.product(for: targetIndustry) {
                primaryButton(
                    label: "\(product.displayPrice) — Unlock the rest of \(config.brand.titleBody)",
                    action: { await buy(product) }
                )
            } else {
                primaryButton(
                    label: "Unlock the rest of \(config.brand.titleBody)",
                    action: { },
                    disabled: true
                )
            }

            if let master = purchases.masterProduct {
                secondaryButton(
                    label: "Unlock all industries — \(master.displayPrice)",
                    action: { await buy(master) }
                )
            }
        }
    }

    private func primaryButton(label: String, action: @escaping () async -> Void, disabled: Bool = false) -> some View {
        Button {
            Task { await action() }
        } label: {
            HStack(spacing: 8) {
                if isPurchasing {
                    ProgressView()
                        .progressViewStyle(.circular)
                        .tint(.white)
                }
                Text(label)
                    .font(.system(size: 16, weight: .semibold, design: .default))
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(config.brand.primaryColor)
            .foregroundStyle(.white)
            .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .disabled(disabled || isPurchasing)
    }

    private func secondaryButton(label: String, action: @escaping () async -> Void) -> some View {
        Button {
            Task { await action() }
        } label: {
            Text(label)
                .font(.system(size: 15, weight: .medium, design: .default))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 13)
                .background(PGColors.card)
                .foregroundStyle(PGColors.ink)
                .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .stroke(PGColors.cardBorder, lineWidth: 1)
                )
        }
        .disabled(isPurchasing)
    }

    // MARK: - Restore + Legal

    private var restoreSection: some View {
        Button {
            Task { await purchases.restorePurchases() }
        } label: {
            Text("Restore Purchases")
                .font(PGFont.buttonLabel)
                .foregroundStyle(PGColors.accent)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 4)
        }
    }

    private var legalSection: some View {
        VStack(spacing: 6) {
            Text("Purchases are one-time and apply to all your devices via your Apple ID.")
                .font(.system(size: 11))
                .foregroundStyle(PGColors.inkLight)
                .multilineTextAlignment(.center)
                .frame(maxWidth: .infinity)

            HStack(spacing: 16) {
                Link("Terms of Use", destination: URL(string: "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/")!)
                Text("·")
                    .foregroundStyle(PGColors.inkFaint)
                Link("Privacy Policy", destination: URL(string: "https://jamesbrowne.dev/privacy")!)
            }
            .font(.system(size: 11, weight: .medium))
            .foregroundStyle(PGColors.accent)
        }
        .padding(.top, 8)
    }

    // MARK: - Actions

    private func buy(_ product: Product) async {
        isPurchasing = true
        let success = await purchases.purchase(product)
        isPurchasing = false
        if success { dismiss() }
    }

    private func loadSampleTerms() async {
        // Load the industry's bundled JSON to: (1) count locked (E–Z) terms
        // for the header subhead, and (2) sample 5 terms specifically from
        // E–Z so the preview shows what's actually behind the paywall.
        let resource = config.brand.dataResource
        guard let url = Bundle.main.url(forResource: resource, withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let terms = try? JSONDecoder().decode([Term].self, from: data) else { return }
        let lockedTerms = terms.filter { !IndustryConfig.freeLetters.contains($0.letter) }
        lockedCount = lockedTerms.count
        // Spread 5 samples across the locked terms for visual variety.
        let stride = max(1, lockedTerms.count / 5)
        let sampled = (0..<5).compactMap { idx -> Term? in
            let i = idx * stride
            return i < lockedTerms.count ? lockedTerms[i] : nil
        }
        sampleTerms = sampled
    }
}
