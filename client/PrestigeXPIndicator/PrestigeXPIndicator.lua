--[[
    Companion to the Prestige core module: listens for PrestigeXP addon messages
    (CHAT_MSG_ADDON) and draws a small XP bar. Install under Interface\AddOns\PrestigeXPIndicator
]]

local ADDON_NAME = ...

local PREFIX = "PrestigeXP"

local bar = CreateFrame("StatusBar", "PrestigeXPIndicatorBar", UIParent)
bar:SetSize(200, 16)
bar:SetPoint("TOP", MinimapCluster, "BOTTOM", 0, -6)
bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
bar:SetStatusBarColor(0.58, 0.22, 0.92)
bar:SetFrameStrata("MEDIUM")
bar:Hide()

local bg = bar:CreateTexture(nil, "BACKGROUND")
bg:SetAllPoints(bar)
bg:SetTexture(0, 0, 0, 0.55)

local border = CreateFrame("Frame", nil, bar)
border:SetPoint("TOPLEFT", bar, -1, 1)
border:SetPoint("BOTTOMRIGHT", bar, 1, -1)
border:SetBackdrop({
    edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
    tile = true,
    tileSize = 8,
    edgeSize = 12,
    insets = { left = 2, right = 2, top = 2, bottom = 2 },
})

local text = bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
text:SetPoint("CENTER", bar, "CENTER", 0, 0)

local function applyMessage(msg)
    if not msg or msg == "" then
        return
    end
    local a, b, c = strsplit(",", msg, 3)
    local cur = tonumber(a)
    local nxt = tonumber(b)
    local pl = tonumber(c) or 0
    if not cur or not nxt or nxt <= 0 then
        bar:Hide()
        return
    end
    bar:SetMinMaxValues(0, nxt)
    bar:SetValue(math.min(cur, nxt))
    bar:Show()
    if BreakUpLargeNumbers then
        text:SetFormattedText("Prestige %u: %s / %s XP", pl, BreakUpLargeNumbers(cur), BreakUpLargeNumbers(nxt))
    else
        text:SetFormattedText("Prestige %u: %u / %u XP", pl, cur, nxt)
    end
end

local f = CreateFrame("Frame")
f:RegisterEvent("ADDON_LOADED")
f:RegisterEvent("CHAT_MSG_ADDON")
f:SetScript("OnEvent", function(_, event, ...)
    if event == "ADDON_LOADED" then
        local name = ...
        if name == ADDON_NAME then
            RegisterAddonMessagePrefix(PREFIX)
        end
    elseif event == "CHAT_MSG_ADDON" then
        local prefix, msg = ...
        if prefix == PREFIX then
            applyMessage(msg)
        end
    end
end)
