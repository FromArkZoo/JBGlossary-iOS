import SwiftUI

struct TermDetailView: View {
    @EnvironmentObject var store: GlossaryStore
    @EnvironmentObject var purchases: PurchaseManager
    let term: Term

    private var isLocked: Bool {
        purchases.isLocked(term, in: store.industryID)
    }

    var body: some View {
        ZStack {
            PGBackground()
            if isLocked {
                // Defense in depth — every upstream navigation path already
                // gates on lock state; this branch covers cross-link injection
                // or future routes that might land a locked term here.
                LockedTermView(term: term, industryID: store.industryID)
            } else {
                ScrollView {
                    VStack(alignment: .leading, spacing: 14) {
                        header
                        if term.hasPlain {
                            plainEnglish
                        }
                        if term.hasSnappy {
                            snappy
                        }
                        definition
                        tags
                        if term.hasSources {
                            sourcesFooter
                        }
                        Spacer(minLength: 24)
                    }
                    .frame(maxWidth: 720, alignment: .leading)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding(.horizontal, 16)
                    .padding(.top, 8)
                }
            }
        }
        .navigationTitle(term.term)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                if !isLocked {
                    Button {
                        store.toggleFavorite(term)
                    } label: {
                        Image(systemName: store.isFavorited(term) ? "star.fill" : "star")
                            .font(.system(size: 19, weight: .semibold))
                            .foregroundStyle(PGColors.accent)
                    }
                    .accessibilityLabel(store.isFavorited(term) ? "Remove from favorites" : "Add to favorites")
                }
            }
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 4) {
            if term.hasCategory {
                Text(term.category)
                    .font(PGFont.eyebrow)
                    .tracking(1.6)
                    .textCase(.uppercase)
                    .foregroundStyle(PGColors.accent)
                    .padding(.top, 14)
            }
            Text(term.term)
                .font(PGFont.termTitle)
                .foregroundStyle(PGColors.ink)
                .lineLimit(2)
                .minimumScaleFactor(0.7)
                .padding(.top, 2)
            if term.hasFull {
                Text(term.full)
                    .font(PGFont.termFullItalic)
                    .foregroundStyle(PGColors.inkLight)
                    .padding(.top, 2)
            }
            Rectangle()
                .fill(PGColors.inkRule)
                .frame(height: 1)
                .padding(.top, 12)
        }
    }

    /// The "headline" line — visually prominent (italic, accent, vertical bar).
    /// When the term has a `plain` line it occupies this slot; otherwise the
    /// `snappy` line gets promoted into the same prominent register.
    private var plainEnglish: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("IN PLAIN ENGLISH")
                .font(PGFont.eyebrow)
                .tracking(2)
                .foregroundStyle(PGColors.inkLight)
            Text(store.attributedPlain(for: term))
                .font(PGFont.snappyItalic)
                .foregroundStyle(PGColors.accent)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.leading, 14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .overlay(alignment: .leading) {
                    Rectangle()
                        .fill(PGColors.accent)
                        .frame(width: 2)
                }
        }
        .padding(.top, 2)
        .padding(.bottom, 6)
    }

    /// Snappy in TWO registers:
    /// - When `plain` exists, snappy is the supporting precise one-liner —
    ///   smaller, ink-light, no bar (the headline role is taken by plain).
    /// - When `plain` is empty, snappy IS the headline and keeps the italic
    ///   accent + vertical bar treatment so legacy entries still look right.
    @ViewBuilder
    private var snappy: some View {
        if term.hasPlain {
            Text(store.attributedSnappy(for: term))
                .font(PGFont.termFullItalic)
                .foregroundStyle(PGColors.inkLight)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.leading, 14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.top, 2)
                .padding(.bottom, 6)
        } else {
            Text(store.attributedSnappy(for: term))
                .font(PGFont.snappyItalic)
                .foregroundStyle(PGColors.accent)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.leading, 14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .overlay(alignment: .leading) {
                    Rectangle()
                        .fill(PGColors.accent)
                        .frame(width: 2)
                }
                .padding(.top, 2)
                .padding(.bottom, 6)
        }
    }

    private var definition: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Definition")
                .font(PGFont.eyebrow)
                .tracking(2)
                .textCase(.uppercase)
                .foregroundStyle(PGColors.inkLight)
            Text(store.attributedDetail(for: term))
                .font(PGFont.body)
                .foregroundStyle(PGColors.ink)
                .lineSpacing(3)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    @ViewBuilder
    private var tags: some View {
        let chips = tagLabels
        if !chips.isEmpty {
            HStack(spacing: 6) {
                ForEach(chips, id: \.self) { label in
                    Text(label.uppercased())
                        .font(.system(size: 10, weight: .semibold))
                        .tracking(0.6)
                        .foregroundStyle(PGColors.accent)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 3)
                        .overlay(
                            Capsule().stroke(PGColors.accent, lineWidth: 1)
                        )
                }
                Spacer()
            }
            .padding(.top, 6)
        }
    }

    private var tagLabels: [String] {
        var labels: [String] = []
        if term.hasCategory { labels.append(term.category) }
        labels.append(contentsOf: term.indications.prefix(2))
        return labels
    }

    private var sourcesFooter: some View {
        Text(LocalizedStringKey(term.sourcesMarkdown))
            .font(.system(size: 11, weight: .regular, design: .serif).italic())
            .foregroundStyle(PGColors.inkFaint)
            .tint(PGColors.accent)
            .padding(.horizontal, 4)
            .padding(.top, 6)
            .accessibilityHint("Source citations. Activate a link to open in browser.")
    }

}

/// Fallback view shown if `TermDetailView` is rendered with a locked term —
/// every upstream path is gated, but this is the safety net. Lets the user
/// jump to the paywall from a clear state.
private struct LockedTermView: View {
    let term: Term
    let industryID: IndustryID
    @EnvironmentObject var purchases: PurchaseManager
    @State private var showingPaywall = false

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "lock.fill")
                .font(.system(size: 36, weight: .light))
                .foregroundStyle(PGColors.inkFaint)
            Text(term.term)
                .font(PGFont.termTitle)
                .foregroundStyle(PGColors.ink)
                .multilineTextAlignment(.center)
            Text("This term is in letters E–Z. Unlock the rest of \(IndustryConfig.config(for: industryID).brand.titleBody) to read it.")
                .font(PGFont.metaItalic)
                .foregroundStyle(PGColors.inkLight)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 28)
            Button {
                showingPaywall = true
            } label: {
                Text("See unlock options")
                    .font(.system(size: 15, weight: .semibold))
                    .padding(.horizontal, 18)
                    .padding(.vertical, 11)
                    .background(IndustryConfig.config(for: industryID).brand.primaryColor)
                    .foregroundStyle(.white)
                    .clipShape(Capsule())
            }
            .padding(.top, 4)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .sheet(isPresented: $showingPaywall) {
            PaywallSheet(targetIndustry: industryID)
                .environmentObject(purchases)
                .presentationDetents([.large])
        }
    }
}
