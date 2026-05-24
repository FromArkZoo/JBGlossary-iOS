import SwiftUI
import StoreKit

/// Root view of JB Glossary. Lists every shipped industry as a tile; every
/// tile opens its industry on tap. Letters A–D are always free; tapping a
/// locked letter (E–Z) inside the industry presents the paywall.
struct IndustryPickerView: View {
    @EnvironmentObject var purchases: PurchaseManager
    let onSelectIndustry: (IndustryID) -> Void

    private let columns = [
        GridItem(.flexible(), spacing: 14),
        GridItem(.flexible(), spacing: 14),
    ]

    var body: some View {
        ZStack {
            PGColors.bg.ignoresSafeArea()
            ScrollView {
                VStack(spacing: 0) {
                    header
                        .padding(.horizontal, 20)
                        .padding(.top, 24)
                        .padding(.bottom, 24)

                    LazyVGrid(columns: columns, spacing: 14) {
                        ForEach(IndustryConfig.all) { config in
                            Button {
                                onSelectIndustry(config.id)
                            } label: {
                                IndustryTile(
                                    config: config,
                                    product: purchases.product(for: config.id),
                                    isUnlocked: purchases.isUnlocked(config.id),
                                    hasMasterUnlock: purchases.hasMasterUnlock
                                )
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 32)
                }
            }
            .scrollIndicators(.hidden)
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(alignment: .firstTextBaseline, spacing: 6) {
                Text("JB")
                    .font(PGFont.jbStamp)
                    .foregroundStyle(PGColors.ink)
                Text("Glossary")
                    .font(PGFont.displayItalic)
                    .foregroundStyle(PGColors.ink)
            }

            Text("Free letters A–D in every industry. Unlock E–Z for $2.99.")
                .font(PGFont.metaItalic)
                .foregroundStyle(PGColors.inkLight)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct IndustryTile: View {
    let config: IndustryConfig
    let product: Product?
    let isUnlocked: Bool
    let hasMasterUnlock: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(config.brand.titleBody)
                .font(PGFont.displayItalic)
                .foregroundStyle(config.brand.primaryColor)
                .lineLimit(1)
                .minimumScaleFactor(0.7)

            Text(priceLabel)
                .font(PGFont.eyebrow)
                .tracking(0.8)
                .foregroundStyle(priceColor)

            Text(config.brand.subtitle)
                .font(PGFont.metaItalic)
                .foregroundStyle(PGColors.inkLight)
                .lineLimit(2)
                .fixedSize(horizontal: false, vertical: true)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(PGColors.card)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(PGColors.cardBorder, lineWidth: 1)
        )
    }

    private var priceLabel: String {
        if hasMasterUnlock { return "UNLOCKED · ALL" }
        if isUnlocked { return "UNLOCKED" }
        let priceText = product?.displayPrice ?? "$2.99"
        return "A–D FREE · \(priceText) FOR E–Z"
    }

    private var priceColor: Color {
        (isUnlocked || hasMasterUnlock) ? config.brand.primaryColor : PGColors.inkLight
    }
}
