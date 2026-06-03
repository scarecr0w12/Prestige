--[[
    Prestige XP bar via AIO + ALE (mod-ale).

    Install: copy this file next to your other ALE scripts (same tree as AIO_Server), e.g.
      env/dist/bin/lua_scripts/z_prestige_aio_xp.lua
    Load order: name must sort AFTER lua_scripts/AIO_Server/AIO.lua so global AIO exists.

    In worldserver.conf / prestige.conf: set Prestige.AddonXpIndicator = 0 to avoid duplicate
    updates if you use this script (the C++ module also sends PrestigeXP addon whispers).
]]

local AIO = rawget(_G, "AIO")
if not AIO then
    print("[z_prestige_aio_xp] Global AIO is nil. Load AIO_Server/AIO.lua before this file (keep z_ prefix or place under a path that sorts later).")
    return
end

-- PLAYER_XP / PLAYER_NEXT_LEVEL_XP indices for WoW 3.3.5a build 12340 (AzerothCore UpdateFields.h).
local PLAYER_XP = 634
local PLAYER_NEXT_LEVEL_XP = 635
local MIN_PRESTIGE_DISPLAY_LEVEL = 80

local PLAYER_EVENT_ON_LOGIN = 3
local PLAYER_EVENT_ON_GIVE_XP = 12
local PLAYER_EVENT_ON_LEVEL_CHANGE = 13

local function canShowPrestigeForPlayer(player)
    return player and player:GetLevel() >= MIN_PRESTIGE_DISPLAY_LEVEL
end

local function getPrestigeLevel(player)
    if not player then
        return 0
    end
    local q = CharDBQuery("SELECT prestigelevel FROM character_prestige_stats WHERE guid = " .. player:GetGUIDLow())
    if not q then
        return 0
    end
    return q:GetUInt32(0)
end

-- Never hold Player across CreateLuaEvent: the userdata is invalidated. Capture GUID and resolve later.
local function sendPrestigeXp(player)
    if not player then
        return
    end
    if not canShowPrestigeForPlayer(player) then
        return
    end
    if not player:IsInWorld() then
        return
    end
    local nxt = player:GetUInt32Value(PLAYER_NEXT_LEVEL_XP)
    if not nxt or nxt == 0 then
        return
    end
    local cur = player:GetUInt32Value(PLAYER_XP)
    local pl = getPrestigeLevel(player)
    AIO.Handle(player, "PrestigeXP", "Update", cur, nxt, pl)
end

local function scheduleSendPrestigeXp(player, delayMs)
    if not player then
        return
    end
    local guid = player:GetGUID()
    CreateLuaEvent(function()
        local p = GetPlayerByGUID(guid)
        sendPrestigeXp(p)
    end, delayMs, 1)
end

if AIO.IsServer() and AIO.IsMainState() then
    RegisterPlayerEvent(PLAYER_EVENT_ON_LOGIN, function(_, player)
        scheduleSendPrestigeXp(player, 100)
    end)

    RegisterPlayerEvent(PLAYER_EVENT_ON_GIVE_XP, function(_, player, amount)
        scheduleSendPrestigeXp(player, 1)
        return amount
    end)

    RegisterPlayerEvent(PLAYER_EVENT_ON_LEVEL_CHANGE, function(_, player)
        scheduleSendPrestigeXp(player, 1)
    end)
end

if AIO.AddAddon() then
    return
end

-- === Client (sent by AIO) ===

local bar = CreateFrame("StatusBar", "PrestigeAIO_XPBar", UIParent)
bar:SetSize(200, 16)
bar:SetPoint("TOP", MinimapCluster, "BOTTOM", 0, -6)
bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
bar:SetStatusBarColor(0.58, 0.22, 0.92)
bar:SetFrameStrata("MEDIUM")
bar:Hide()

local bg = bar:CreateTexture(nil, "BACKGROUND")
bg:SetAllPoints(bar)
bg:SetTexture(0, 0, 0, 0.55)

local text = bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
text:SetPoint("CENTER", bar, "CENTER", 0, 0)

local function isPrestigeDisplayLevelClient()
    return (UnitLevel("player") or 0) >= MIN_PRESTIGE_DISPLAY_LEVEL
end

local clientEvents = CreateFrame("Frame")
clientEvents:RegisterEvent("PLAYER_ENTERING_WORLD")
clientEvents:RegisterEvent("PLAYER_LEVEL_UP")
clientEvents:SetScript("OnEvent", function()
    if not isPrestigeDisplayLevelClient() then
        bar:Hide()
    end
end)

AIO.AddHandlers("PrestigeXP", {
    Update = function(_, cur, nxt, pl)
        cur = tonumber(cur) or 0
        nxt = tonumber(nxt) or 0
        pl = tonumber(pl) or 0
        if nxt <= 0 or not isPrestigeDisplayLevelClient() then
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
    end,
})
